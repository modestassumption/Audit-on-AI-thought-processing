"""Loaders for the three source datasets, normalised to one row shape.

Every loader returns a list of dicts with keys:
    question (str), options (list[str] of length 4), answer (letter A-D)
plus whatever identifying fields the source provides.
"""

from __future__ import annotations

from datasets import load_dataset

LETTERS = "ABCD"

MMLU_REPO = "cais/mmlu"
GLOBAL_MMLU_REPO = "CohereLabs/Global-MMLU"
SARVAM_REPO = "sarvamai/mmlu-indic"


def load_mmlu(revision: str | None = None) -> list[dict]:
    """English MMLU test set, with sample_id matching Global-MMLU's `{subject}/test/{idx}`."""
    ds = load_dataset(MMLU_REPO, "all", split="test", revision=revision)
    rows, counters = [], {}
    for r in ds:
        idx = counters.get(r["subject"], 0)
        counters[r["subject"]] = idx + 1
        rows.append(
            {
                "sample_id": f"{r['subject']}/test/{idx}",
                "subject": r["subject"],
                "question": r["question"],
                "options": list(r["choices"]),
                "answer": LETTERS[r["answer"]],
            }
        )
    return rows


def load_global_mmlu(lang: str, revision: str | None = None) -> list[dict]:
    ds = load_dataset(GLOBAL_MMLU_REPO, lang, split="test", revision=revision)
    return [
        {
            "sample_id": r["sample_id"],
            "subject": r["subject"],
            "subject_category": r["subject_category"],
            "question": r["question"],
            "options": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
            "answer": r["answer"].strip(),
            "cultural_sensitivity_label": r["cultural_sensitivity_label"],
            "is_annotated": r["is_annotated"],
        }
        for r in ds
    ]


def load_sarvam(lang: str, revision: str | None = None) -> list[dict]:
    """Sarvam mmlu-indic rows. No ids; `row` is the position, shared across language configs."""
    ds = load_dataset(SARVAM_REPO, lang, split="test", revision=revision)
    return [
        {
            "row": i,
            "question": r["question"],
            "options": list(r["choices"]),
            "answer": LETTERS[r["answer"]],
        }
        for i, r in enumerate(ds)
    ]
