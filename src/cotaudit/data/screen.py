"""Structural screen for machine-translated (Sarvam) Malayalam questions.

Sarvam's mmlu-indic often keeps only one paragraph of a multi-line question, so passages,
premises, numbered statements and formulas disappear and the Malayalam question can no longer be
answered. An unanswerable question pushes models toward the hinted option for reasons unrelated
to faithfulness, so it would bias the language comparison (H2).

The 60-question native-speaker review samples the problem; this screen applies deterministic
rules to every question so the same kind of damage is caught everywhere. Flagged questions are
excluded and replaced from the reserve (which is screened the same way). The rules only look at
structure, never at meaning, and every flag records its reason in data/manifest.json.
"""

from __future__ import annotations

import re

MALAYALAM = re.compile(r"[ഀ-ൿ]")
LATIN = re.compile(r"[A-Za-z]")
# Formal-logic and set notation that a translation must carry over unchanged.
SYMBOLS = "⊃≡∨·~∧¬→↔∀∃⊢"

MIN_EN_CHARS = 80        # length rule applies only to questions at least this long
MIN_LENGTH_RATIO = 0.5   # Malayalam text is usually longer than English; half is a clear loss
MIN_LINES = 3            # a "multi-line" English question has at least this many non-empty lines
COLLAPSE_RATIO = 0.8     # ...and its translation collapsed to one line *and* lost text
MIN_ML_SHARE = 0.3       # share of Malayalam letters among all letters in the question
MAX_REPEATS = 8          # same word this many times in a row = degenerate translation loop

APPROX = re.compile(r"~(?=\s*\d)")   # "~30 pixels" means "about", not negation
REPEAT = re.compile(r"(\S+)(?:[\s,]+\1){%d,}" % (MAX_REPEATS - 1))


def _lines(text: str) -> int:
    return sum(1 for ln in text.splitlines() if ln.strip())


def screen_ml(en: dict, ml: dict) -> list[str]:
    """Reasons the Malayalam version looks structurally broken; empty if it passes."""
    eq, mq = en["question"].strip(), ml["question"].strip()
    reasons = []

    ratio = len(mq) / max(1, len(eq))
    if len(eq) >= MIN_EN_CHARS and ratio < MIN_LENGTH_RATIO:
        reasons.append(f"question shortened to {ratio:.2f}x the English length")

    en_lines, ml_lines = _lines(eq), _lines(mq)
    if en_lines >= MIN_LINES and ml_lines * 2 <= en_lines and ratio < COLLAPSE_RATIO:
        reasons.append(f"multi-line question collapsed ({en_lines} -> {ml_lines} lines)")

    if REPEAT.search(mq) or any(REPEAT.search(o) for o in ml["options"]):
        reasons.append("repetition loop")

    eq_sym, mq_sym = APPROX.sub("", eq), APPROX.sub("", mq)
    lost = {s: eq_sym.count(s) - mq_sym.count(s) for s in SYMBOLS if eq_sym.count(s) > mq_sym.count(s)}
    if lost:
        reasons.append("lost symbols " + " ".join(f"{s}x{n}" for s, n in sorted(lost.items())))

    m, latin = len(MALAYALAM.findall(mq)), len(LATIN.findall(mq))
    if len(LATIN.findall(eq)) > 20 and m / max(1, m + latin) < MIN_ML_SHARE:
        reasons.append("question left untranslated")

    opts = ml["options"]
    if len(opts) != 4 or any(not o.strip() for o in opts):
        reasons.append("missing or empty options")
    return reasons
