"""Seeded, stratified question selection and hinted-answer assignment."""

from __future__ import annotations

import random

from cotaudit.data.load import LETTERS


def eligible_pool(
    global_mmlu: dict[str, dict[str, dict]],
    mmlu: dict[str, dict],
    ml_matched: dict[str, dict],
    label: str,
) -> list[str]:
    """sample_ids that are culturally agnostic, present in all four languages, with agreeing keys."""
    pool = []
    for sid, row in global_mmlu["en"].items():
        if row["cultural_sensitivity_label"] != label or sid not in ml_matched:
            continue
        answers = {mmlu[sid]["answer"], ml_matched[sid]["answer"]}
        answers |= {global_mmlu[lang][sid]["answer"] for lang in global_mmlu}
        if len(answers) == 1:
            pool.append(sid)
    return sorted(pool)


def stratified_sample(
    pool: list[str], category_of: dict[str, str], strata: dict[str, list[str]], n: int, seed: int
) -> tuple[list[str], list[str]]:
    """Pick n/len(strata) ids per stratum. Returns (selected, reserve), both in seeded order.

    The reserve holds every other eligible id, shuffled, for replacing bad translations.
    """
    per_stratum = n // len(strata)
    rng = random.Random(seed)
    selected, reserve = [], []
    for categories in strata.values():
        ids = [sid for sid in pool if category_of[sid] in categories]
        if len(ids) < per_stratum:
            raise ValueError(f"Only {len(ids)} eligible questions for {categories}")
        rng.shuffle(ids)
        selected += ids[:per_stratum]
        reserve += ids[per_stratum:]
    return selected, reserve


def stratum_of(category: str, strata: dict[str, list[str]]) -> str:
    for name, categories in strata.items():
        if category in categories:
            return name
    raise KeyError(category)


def hinted_letter(sample_id: str, gold: str, seed: int) -> str:
    """A wrong option chosen at random, fixed per question regardless of selection order."""
    wrong = [c for c in LETTERS if c != gold]
    return random.Random(f"{seed}:{sample_id}").choice(wrong)
