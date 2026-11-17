"""Sample size and power (proposal 4.7, "Sample size"; owner: sub-team D).

`planning_table` reproduces the proposal's table: the smallest difference in faithfulness each
main comparison can detect, for a given influence rate and number of questions. `pilot_check`
applies the proposal's rule to the runs logged so far: a model whose hints change fewer than
15% of its answers is raised from 300 to 450 questions.

Like the proposal, the formulas treat runs as independent. Questions repeat across cells (the
regression handles that with GEE), so the real detectable differences are somewhat larger.
"""

from __future__ import annotations

import math
from statistics import NormalDist

import pandas as pd

from cotaudit.analysis.influence import wilson

HINTS_PER_LANGUAGE = 3  # expert, metadata, leaked in the question's language (H4 runs not counted)
PLANNED, RAISED, THRESHOLD = 300, 450, 0.15

_z = NormalDist().inv_cdf


def min_detectable_difference(n_per_group: float, p: float = 0.5, alpha: float = 0.05,
                              power: float = 0.8, comparisons: int = 1) -> float:
    """Smallest difference between two independent proportions near p that a two-sided test
    detects with the given power, with alpha split over `comparisons` (Bonferroni, which is
    also the first step of Holm)."""
    if n_per_group <= 0:
        return math.nan
    return (_z(1 - alpha / (2 * comparisons)) + _z(power)) * math.sqrt(2 * p * (1 - p) / n_per_group)


def ci_half_width(n: float, p: float = 0.5, level: float = 0.95) -> float:
    """Half-width of a normal-approximation confidence interval for a rate near p."""
    if n <= 0:
        return math.nan
    return _z(0.5 + level / 2) * math.sqrt(p * (1 - p) / n)


def planning_table(influence_rate: float = 0.25, n_questions: int = PLANNED, n_models: int = 3,
                   n_languages: int = 4, faithfulness: float = 0.5, alpha: float = 0.05,
                   power: float = 0.8) -> pd.DataFrame:
    """The proposal's sample-size table (section 4.7).

    Language comparisons are adjusted for the tests against English and model comparisons for
    the model pairs. Comparisons inside one model are not adjusted, as in the proposal. One
    model x language x hint is reported descriptively, by the half-width of its interval.
    """
    cell = influence_rate * n_questions * HINTS_PER_LANGUAGE  # influenced runs, one model x language
    model_pairs = n_models * (n_models - 1) // 2

    def mdd(n: float, comparisons: int) -> float:
        return min_detectable_difference(n, faithfulness, alpha, power, comparisons)

    rows = [
        ("two languages, all models together", cell * n_models, n_languages - 1,
         mdd(cell * n_models, n_languages - 1), math.nan),
        ("two models, all languages together", cell * n_languages, model_pairs,
         mdd(cell * n_languages, model_pairs), math.nan),
        ("two languages within one model", cell, 1, mdd(cell, 1), math.nan),
        ("one model, language and hint type", influence_rate * n_questions, None, math.nan,
         ci_half_width(influence_rate * n_questions, faithfulness)),
    ]
    return pd.DataFrame(rows, columns=["comparison", "influenced per group", "alpha split over",
                                       "detectable difference", "ci half-width"])


def pilot_check(hinted: pd.DataFrame, threshold: float = THRESHOLD, planned: int = PLANNED,
                raised: int = RAISED) -> pd.DataFrame:
    """Each model's influence rate so far and the number of questions the proposal's rule asks for.

    Uses same-language hints only (as the planning table does) and determined runs only (as
    `scripts/report_runs.py` does). The projection scales the observed rate and the share of
    determined runs to the recommended number of questions.
    """
    same = hinted[hinted["hint_lang"] == hinted["lang"]]
    rows = []
    for model, g in same.groupby("model"):
        det = g[~g["undetermined"]]
        k, n = int(det["influenced"].sum()), len(det)
        rate = k / n if n else math.nan
        lo, hi = wilson(k, n)
        questions = raised if rate < threshold else planned  # NaN rate (nothing determined): planned
        per_language = rate * (n / len(g)) * questions * HINTS_PER_LANGUAGE if n else math.nan
        rows.append({
            "model": model, "questions so far": g["qid"].nunique(), "hinted runs": len(g),
            "determined": n, "influenced": k, "influence rate": rate, "ci low": lo, "ci high": hi,
            "questions needed": questions, "influenced per language (projected)": per_language,
            "detectable difference within the model": min_detectable_difference(per_language)
            if n else math.nan,
            "note": f"interval includes {threshold:.0%}: decide after more runs" if lo < threshold < hi else "",
        })
    return pd.DataFrame(rows)
