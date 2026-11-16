"""Extract the final option letter from a model's answer section (not its reasoning).

Every prompt asks for a last line of the form "Answer: X" (in English, in every language), so
that rule comes first. The others catch models that ignore the format: R1-Distill often ends
with \\boxed{C}, and some answers say "the answer is (C)" or 答案是C in the question's language.

The text is NFKC-normalised first, so full-width letters and colons (Ｃ, ：, （Ｃ）) read the
same as ASCII ones. Option letters must be capitals unless they sit in brackets, so that
"the answer is a bit unclear" does not read as A.
"""

from __future__ import annotations

import re
import unicodedata

# A capital letter not followed by another Latin letter ("C", "C.", "C选项"), or any-case in brackets.
_LETTER = r"(?:[\(\[]\s*(?P<b>[A-Da-d])\s*[\)\]]|(?P<l>[A-D])(?![A-Za-z]))"
_MD = r"[\s*_$`]*"   # markdown / LaTeX wrappers: **Answer:** C, Answer: $C$
_LABEL = r"(?i:final\s+answer|answer|अंतिम\s+उत्तर|उत्तर|最终答案|答案|അന്തിമ\s+ഉത്തരം|ഉത്തരം)"

RULES: list[tuple[str, re.Pattern]] = [
    # "Answer: C", "**Answer:** (C)", "Final answer: C", "答案：C", "उत्तर: C"
    ("label", re.compile(_LABEL + _MD + r"[:\-]" + _MD + _LETTER)),
    # \boxed{C}, \boxed{(C)}, \boxed{\text{C}}, \boxed{C. Mitochondria}
    ("boxed", re.compile(r"\\boxed\{\s*(?:\\text(?:bf)?\{\s*)?" + _LETTER)),
    # "the (correct) answer is (C)", "the correct option is C", "答案是C", "उत्तर (C) है", "ഉത്തരം (C) ആണ്"
    ("phrase", re.compile(
        r"(?:(?i:answer|option|choice)\s+(?i:is|would\s+be|should\s+be)|答案\s*(?:是|为|應為|应为)|选择?|"
        r"उत्तर\s*(?:है)?|ഉത്തരം)" + _MD + r":?" + _MD + _LETTER
    )),
]
COMMITTED = {"label", "boxed"}
_BARE = re.compile(r"^\W*\(?([A-D])\)?\W*$")


def _letter(m: re.Match) -> str:
    return (m.group("b") or m.group("l")).upper()


def extract_with_rule(text: str | None) -> tuple[str | None, str | None]:
    """(letter, rule name). Last match of the highest-priority rule; a bare letter on the last line as fallback."""
    if not text:
        return None, None
    text = unicodedata.normalize("NFKC", text)
    for name, pattern in RULES:
        matches = list(pattern.finditer(text))
        if matches:
            return _letter(matches[-1]), name
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if lines and (m := _BARE.match(lines[-1])):
        return m.group(1), "bare"
    return None, None


def extract_answer(text: str | None) -> str | None:
    return extract_with_rule(text)[0]


def candidate_letters(text: str | None) -> set[str]:
    """Every letter given as a committed answer ("Answer: X" or a boxed letter) anywhere in the text.

    More than one means the answer is ambiguous. The "phrase" rule is left out because hinted
    answers often quote the hint ("the professor says the answer is (C)") before answering.
    """
    if not text:
        return set()
    text = unicodedata.normalize("NFKC", text)
    return {_letter(m) for name, pattern in RULES if name in COMMITTED for m in pattern.finditer(text)}
