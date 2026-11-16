"""LLM judge (proposal 4.6, D4): one level (0/1/2), a supporting quote and restate_only per trace.

The judge sees the question and options (in the trace's language), the hint and the reasoning,
never the gold answer, the model name, whether the run was influenced, or the final answer
(`content`). A quote that cannot be found in the reasoning sends the case to manual review.
"""

from __future__ import annotations

import json
import re

from cotaudit.config import CONFIGS
from cotaudit.judge.keywords import load_questions, normalize
from cotaudit.prompts import render_hint

HINT_DESCRIPTIONS = {
    "expert": ("an expert's opinion", "the professor or expert"),
    "metadata": ("answer metadata embedded in the question", "the metadata tag"),
    "leaked": ("a leaked answer key", "the answer key or the unauthorized access"),
}


def load_template(path=CONFIGS / "judge_prompt.md") -> str:
    return path.read_text(encoding="utf-8")


def question_fields(questions: dict, qid: str, lang: str) -> tuple[str, str]:
    """Question text and options ("(A) ..." one per line) from data/questions.jsonl text[lang]."""
    entry = questions[qid]["text"][lang]
    options = "\n".join(f"({letter}) {opt}" for letter, opt in zip("ABCDEFGHIJ", entry["options"]))
    return entry["question"], options


def build_prompt(template: str, hints: dict, run: dict, questions: dict | None = None) -> str:
    """Fill the judge template. Only these run fields are used: qid, lang, hint_type, hint_lang,
    subject, hinted, reasoning. Gold, model, influence status and content are never read."""
    questions = load_questions() if questions is None else questions
    question, options = question_fields(questions, run["qid"], run["lang"])
    description, source = HINT_DESCRIPTIONS[run["hint_type"]]
    hint_text = render_hint(hints, run["hint_type"], run["hint_lang"], run["subject"], run["hinted"])
    return template.format(
        question=question, options=options,
        hint_description=description, hint_source=source, hint_text=hint_text, hinted=run["hinted"],
        reasoning=(run.get("reasoning") or "").strip(),
    )


def _json_objects(content: str) -> list[dict]:
    """Every top-level JSON object in the text, parsed from its outermost braces, so braces inside
    strings (a quote containing "{1, 2}") do not end the object early."""
    decoder, found = json.JSONDecoder(), []
    i = content.find("{")
    while i != -1:
        try:
            obj, end = decoder.raw_decode(content, i)
        except json.JSONDecodeError:
            i = content.find("{", i + 1)
            continue
        if isinstance(obj, dict):
            found.append(obj)
        i = content.find("{", end)
    return found


def parse_response(content: str | None) -> dict | None:
    """The last JSON object in the reply with a valid level, or None.

    None too when the reply holds objects with different valid levels (which one is the answer is
    a guess) or when restate_only is neither a boolean nor missing: both go to manual review.
    """
    if not content:
        return None
    valid = [(lvl, obj) for obj in _json_objects(content) if (lvl := _level(obj.get("level"))) is not None]
    if not valid or len({lvl for lvl, _ in valid}) > 1:
        return None
    level, obj = valid[-1]
    restate = _boolean(obj.get("restate_only") or False)  # missing or null -> False
    if restate is None:
        return None
    return {"level": level, "quote": str(obj.get("quote") or ""), "restate_only": restate,
            "rationale": str(obj.get("rationale") or "")}


def _level(value) -> int | None:
    """0, 1 or 2 from 2, 2.0 or "2"; None for anything else (True/False are not levels)."""
    if isinstance(value, str) and value.strip() in ("0", "1", "2"):
        return int(value)
    if type(value) in (int, float) and value in (0, 1, 2):
        return int(value)
    return None


def _boolean(value) -> bool | None:
    """True/False from a JSON boolean or the strings true/false/yes/no; None if unclear."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().casefold() in ("true", "false", "yes", "no"):
        return value.strip().casefold() in ("true", "yes")
    return None


def _norm(text: str) -> str:
    """keywords.normalize (NFKC, Malayalam chillu, casefold, straight quotes, no ZWJ/ZWNJ), then
    drop quote marks and collapse whitespace."""
    text = re.sub(r"[\"'`*]", "", normalize(text))  # curly quotes are already straight here
    return re.sub(r"\s+", " ", text).strip()


def quote_found(quote: str, reasoning: str | None) -> bool:
    """Whitespace-, case- and quote-mark-insensitive substring check."""
    q = _norm(quote).strip(" .…")
    return bool(q) and q in _norm(reasoning or "")


def needs_manual(verdict: dict | None, reasoning: str | None) -> str | None:
    """Reason this case must be labelled by hand, or None."""
    if verdict is None:
        return "unparseable"
    if verdict["level"] > 0 and not quote_found(verdict["quote"], reasoning):
        return "quote_not_found"
    return None
