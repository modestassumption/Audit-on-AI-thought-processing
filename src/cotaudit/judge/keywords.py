"""Keyword filter: flag reasoning that may mention the hint (configs/keywords.yaml, decisions D1/D2).

Every trace is checked against all four language lists. Each hit is one record:
term, list_lang, tier (strong/weak), q_overlap (the term also occurs in the question or options in
the trace's language, so it counts as weak) and relation (question_lang / hint_lang / other).
"""

from __future__ import annotations

import json
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
    """NFKC, atomic Malayalam chillu, casefold, straight quotes, drop ZWJ/ZWNJ. For terms and text."""
    text = unicodedata.normalize("NFKC", text or "")
    text = _CHILLU.sub(lambda m: _CHILLU_MAP[m.group(1)], text)
    return text.casefold().translate(_CURLY_QUOTES).translate(_ZERO_WIDTH)


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
    norm, norm_q = normalize(text), normalize(question)
    return [
        {"term": term, "list_lang": list_lang, "tier": tier,
         "q_overlap": bool(norm_q) and term_matches(term, list_lang, norm_q),
         "relation": relation(list_lang, lang, hint_lang)}
        for term, list_lang, tier in term_lists(keywords, hint_type)
        if term_matches(term, list_lang, norm)
    ]


def keyword_hits(reasoning: str | None, keywords: dict, hint_type: str, langs: set[str]) -> list[str]:
    """Legacy view: sorted terms (wildcard dropped) of every hit, any tier.

    `langs` is kept for compatibility only; all four lists now run on every trace (D2).
    """
    hits = find_hits(reasoning, keywords, hint_type, lang="")
    return sorted({h["term"].rstrip("*") for h in hits})
