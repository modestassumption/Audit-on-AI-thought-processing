"""Extract the final option letter from a model's answer section (not its reasoning)."""

from __future__ import annotations

import re

_LABEL = r"(?:answer|final answer|उत्तर|अंतिम उत्तर|答案|最终答案|ഉത്തരം|അന്തിമ ഉത്തരം)"
_PATTERNS = [
    # "Answer: C", "**Answer:** (C)", "答案：C"
    re.compile(_LABEL + r"\s*\**\s*[:：]\s*\**\s*[\(\[]?\s*([A-D])\b", re.IGNORECASE),
    # \boxed{C}
    re.compile(r"\\boxed\{\s*\(?([A-D])\)?\s*\}"),
    # "the answer is (C)"
    re.compile(r"answer is\s*\**\s*[\(\[]?([A-D])\b", re.IGNORECASE),
]
_BARE = re.compile(r"^\W*\(?([A-D])\)?\W*$")


def extract_answer(text: str | None) -> str | None:
    """Last match of the highest-priority pattern; a bare letter on the last line as fallback."""
    if not text:
        return None
    for pattern in _PATTERNS:
        matches = pattern.findall(text)
        if matches:
            return matches[-1].upper()
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if lines and (m := _BARE.match(lines[-1])):
        return m.group(1)
    return None
