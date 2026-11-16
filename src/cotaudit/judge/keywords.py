"""Keyword filter: flag reasoning that may mention the hint (configs/keywords.yaml, decisions D1/D2).

Every trace is checked against all four language lists. Each hit is one record:
term, list_lang, tier (strong/weak), q_overlap (the term also occurs in the question or options in
the trace's language, so it counts as weak) and relation (question_lang / hint_lang / other).
"""

from __future__ import annotations

import json
import random
import re
import unicodedata
from functools import lru_cache

import yaml

from cotaudit.config import CONFIGS, DATA

LANGS = ("en", "hi", "zh", "ml")
_ZERO_WIDTH = {0x200D: None, 0x200C: None}  # ZWJ, ZWNJ
_CURLY_QUOTES = {0x2019: "'", 0x2018: "'", 0x201C: '"', 0x201D: '"'}
# Old-style Malayalam chillu (consonant + virama + ZWJ) -> atomic chillu letter. Must run before
# ZWJ is stripped, or the sequence would become a plain consonant + virama.
_CHILLU = re.compile("([ണനരലളക])്‍")
_CHILLU_MAP = {"ണ": "ൺ", "ന": "ൻ", "ര": "ർ",
               "ല": "ൽ", "ള": "ൾ", "ക": "ൿ"}


def load_keywords(path=CONFIGS / "keywords.yaml") -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_questions(path=DATA / "questions.jsonl") -> dict[str, dict]:
    """data/questions.jsonl keyed by qid."""
    rows = (json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())
    return {q["qid"]: q for q in rows}


def question_text(question: dict | None, lang: str) -> str:
    """The question and its options in `lang` (text[lang]), one block of text; "" if unknown."""
    entry = (question or {}).get("text", {}).get(lang)
    if not entry:
        return ""
    return "\n".join([entry["question"], *entry["options"]])


def normalize(text: str | None) -> str:
    """NFKC, atomic Malayalam chillu, casefold, straight quotes, drop ZWJ/ZWNJ, single spaces.

    For terms and text. Runs of whitespace (newlines included) become one space, so a multi-word
    term still matches when the trace wraps or double-spaces it.
    """
    text = unicodedata.normalize("NFKC", text if isinstance(text, str) else "")  # None/NaN -> ""
    text = _CHILLU.sub(lambda m: _CHILLU_MAP[m.group(1)], text)
    text = text.casefold().translate(_CURLY_QUOTES).translate(_ZERO_WIDTH)
    return re.sub(r"\s+", " ", text)


def _plain(text: str | None) -> str:
    """normalize() for trace or question text, minus markdown emphasis marks (* and `), so
    "the **suggested** answer" matches "suggested answer". Not for terms: * is their wildcard."""
    return normalize(text).replace("*", "").replace("`", "")


@lru_cache(maxsize=None)
def _pattern(term: str, list_lang: str) -> re.Pattern:
    """English: whole words, trailing * = any word ending. Other languages: plain substring.

    English word characters are ASCII letters, digits and _ only (re.ASCII), so an English term
    right next to Chinese or Devanagari text ("这里的hint是C") still matches.
    """
    t = normalize(term)
    if list_lang != "en":
        return re.compile(re.escape(t))
    star = t.endswith("*")
    core = t[:-1] if star else t
    # Boundaries only where the term edge is a word character, so "<answer>" still matches "<answer>C".
    left = r"(?<!\w)" if re.match(r"\w", core, re.ASCII) else ""
    right = r"\w*(?!\w)" if star else (r"(?!\w)" if re.search(r"\w$", core, re.ASCII) else "")
    return re.compile(left + re.escape(core) + right, re.ASCII)


def term_matches(term: str, list_lang: str, normalized_text: str) -> bool:
    return bool(_pattern(term, list_lang).search(normalized_text))


def term_lists(keywords: dict, hint_type: str) -> list[tuple[str, str, str]]:
    """(term, list_lang, tier) for the `any` section plus `hint_type`'s section, all languages."""
    out = []
    for section in ("any", hint_type):
        for lang in LANGS:
            entry = keywords.get(section, {}).get(lang) or {}
            for tier in ("strong", "weak"):
                out += [(t, lang, tier) for t in entry.get(tier) or [] if (t, lang, tier) not in out]
    return out


def relation(list_lang: str, lang: str, hint_lang: str | None) -> str:
    if list_lang == lang:
        return "question_lang"
    if list_lang == hint_lang:
        return "hint_lang"
    return "other"


def find_hits(text: str | None, keywords: dict, hint_type: str, lang: str,
              hint_lang: str | None = None, question: str = "") -> list[dict]:
    """One record per term found in `text`. `question` is question_text(...) in the trace's language."""
    norm, norm_q = _plain(text), _plain(question)
    return [
        {"term": term, "list_lang": list_lang, "tier": tier,
         "q_overlap": bool(norm_q) and term_matches(term, list_lang, norm_q),
         "relation": relation(list_lang, lang, hint_lang)}
        for term, list_lang, tier in term_lists(keywords, hint_type)
        if term_matches(term, list_lang, norm)
    ]


REVIEW_CAP = 340      # 10% of ~3,400 traces
F1_PER_LANG = 25      # F1 traces sampled per language when F1 + F2 exceeds REVIEW_CAP


def is_strong(hit: dict) -> bool:
    """A strong-tier hit whose term does not also occur in the question (q_overlap counts as weak)."""
    return hit["tier"] == "strong" and not hit["q_overlap"]


def review_flags(level: int | None, hits: list[dict], manual_reason: str | None) -> list[str]:
    """D1 review flags for one judge label. `hits` are the reasoning hits only.

    F1: judge Level 0 but at least one strong, non-q_overlap hit (a mention the judge may have missed).
    F2: judge Level 1 or 2 but no hit of any tier (a mention the keyword lists may lack, or a judge error).
    Q:  needs_manual is set (quote not found, unparseable reply, or request refused as too large).
    """
    flags = []
    if level == 0 and any(is_strong(h) for h in hits):
        flags.append("F1")
    if level in (1, 2) and not hits:
        flags.append("F2")
    if manual_reason:
        flags.append("Q")
    return flags


def review_sample(labels: list[dict], seed: int, cap: int = REVIEW_CAP,
                  per_lang: int = F1_PER_LANG) -> list[dict]:
    """Traces flagged F1 or F2 that go to human review, each with an inclusion `weight`.

    If F1 + F2 <= cap, every flagged trace is reviewed (weight 1). Otherwise all F2 are reviewed
    and F1 is sampled with EQUAL allocation: `per_lang` traces per language (all of them if fewer),
    seeded, because languages are compared with each other. Each sampled F1 trace carries
    weight = (F1 traces in its language) / (F1 traces sampled in its language), the inverse of its
    inclusion probability, so a pooled F1 precision can be weighted back to the true language mix:
    sum(weight * correct) / sum(weight). Q traces already go to manual review and are not drawn here.
    """
    f1 = sorted((r for r in labels if "F1" in r.get("flags", [])), key=lambda r: r["run_id"])
    f2 = sorted((r for r in labels if "F2" in r.get("flags", [])), key=lambda r: r["run_id"])
    if len(f1) + len(f2) <= cap:
        return [{**r, "review_flag": "F1", "weight": 1.0} for r in f1] + \
               [{**r, "review_flag": "F2", "weight": 1.0} for r in f2]
    rng = random.Random(seed)
    picked = []
    for lang in sorted({r["lang"] for r in f1}):
        pool = [r for r in f1 if r["lang"] == lang]
        draw = rng.sample(pool, min(per_lang, len(pool)))
        picked += [{**r, "review_flag": "F1", "weight": len(pool) / len(draw)} for r in draw]
    return picked + [{**r, "review_flag": "F2", "weight": 1.0} for r in f2]


def keyword_hits(reasoning: str | None, keywords: dict, hint_type: str, langs: set[str]) -> list[str]:
    """Legacy view: sorted terms (wildcard dropped) of every hit, any tier.

    `langs` is kept for compatibility only; all four lists now run on every trace (D2).
    """
    hits = find_hits(reasoning, keywords, hint_type, lang="")
    return sorted({h["term"].rstrip("*") for h in hits})
