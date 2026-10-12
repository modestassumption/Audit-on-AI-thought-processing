"""Cross-language matching.

Global-MMLU (en/hi/zh) shares MMLU's `sample_id`, so those join directly.
Sarvam mmlu-indic has no ids, but its `en` and `ml` configs are row-aligned, so a
Malayalam row is matched by finding its Sarvam-English twin in MMLU by text.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[^\w]+", " ", text)
    return " ".join(text.split())


def text_key(question: str, options: list[str]) -> str:
    return "\x1f".join([normalise(question), *(normalise(o) for o in options)])


def match_sarvam_to_mmlu(
    mmlu: list[dict], sarvam_en: list[dict], sarvam_other: list[dict]
) -> dict[str, dict]:
    """Return {sample_id: sarvam_other row} for rows that match MMLU unambiguously.

    A match requires: identical normalised question + options text, a key that is
    unique on both sides, and the same answer letter in MMLU, Sarvam-en and Sarvam-other.
    """
    if len(sarvam_en) != len(sarvam_other):
        raise ValueError(
            f"Sarvam configs are not row-aligned: {len(sarvam_en)} vs {len(sarvam_other)}"
        )

    by_key: dict[str, list[dict]] = defaultdict(list)
    for r in mmlu:
        by_key[text_key(r["question"], r["options"])].append(r)
    sarvam_by_key: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(sarvam_en):
        sarvam_by_key[text_key(r["question"], r["options"])].append(i)

    matched = {}
    for key, idxs in sarvam_by_key.items():
        hits = by_key.get(key, [])
        if len(idxs) != 1 or len(hits) != 1:
            continue
        en, other, m = sarvam_en[idxs[0]], sarvam_other[idxs[0]], hits[0]
        if en["answer"] == other["answer"] == m["answer"]:
            matched[m["sample_id"]] = other
    return matched
