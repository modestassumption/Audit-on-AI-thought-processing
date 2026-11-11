"""Malayalam review sheet (data/review/ml_review_60.csv).

The sheet is rewritten by build_dataset.py, so reviewer columns (verdict, reviewer, notes) are
read back first and carried over by qid. The sample is drawn from the seeded selection *before*
exclusions, so excluding a question never changes which 60 questions are under review.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

VERDICT = "verdict(ok/bad)"
HEADER = ["qid", "subject", "gold", "en_question", "en_options", "ml_question", "ml_options",
          VERDICT, "reviewer", "notes"]
REVIEWER_COLS = (VERDICT, "reviewer", "notes")


def review_sample(qid_stratum: dict[str, str], strata: list[str], n: int, seed: int) -> list[str]:
    """n qids, an equal share from each stratum (in the given order), in a fixed order."""
    rng = random.Random(f"{seed}:ml_review")
    names = strata
    per = n // len(names)
    out = []
    for name in names:
        ids = sorted(q for q, s in qid_stratum.items() if s == name)
        out += sorted(rng.sample(ids, per))
    return out


def read_reviewer_columns(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["qid"]: {c: r.get(c) or "" for c in REVIEWER_COLS} for r in csv.DictReader(f)}


def write_review(path: Path, records: list[dict]) -> None:
    """records: question records (as in questions.jsonl). Keeps existing reviewer columns."""
    kept = read_reviewer_columns(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for q in records:
            prev = kept.get(q["qid"], {})
            en, ml = q["text"]["en"], q["text"]["ml"]
            w.writerow([
                q["qid"], q["subject"], q["gold"],
                en["question"], " | ".join(en["options"]),
                ml["question"], " | ".join(ml["options"]),
                *(prev.get(c, "") for c in REVIEWER_COLS),
            ])


def bad_verdicts(path: Path) -> set[str]:
    return {q for q, r in read_reviewer_columns(path).items() if r[VERDICT].strip().lower() == "bad"}
