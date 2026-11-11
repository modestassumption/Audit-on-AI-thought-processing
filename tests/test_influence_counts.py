"""D7 reporting edge cases the fixtures do not cover (in-memory records)."""

import pandas as pd

from cotaudit.analysis.influence import influence_counts, noise_rate, with_influence


def run(qid, hint_type, answer, rep=1, lang="en", hinted="B"):
    return {"model": "m", "qid": qid, "lang": lang, "hint_type": hint_type, "rep": rep,
            "hint_lang": None if hint_type == "none" else lang, "answer": answer, "hinted": hinted,
            "condition": "none" if hint_type == "none" else hint_type}


DF = pd.DataFrame([
    run("q1", "none", "A", 1), run("q1", "none", "A", 2), run("q1", "expert", "B"),  # influenced
    run("q2", "none", "B", 1), run("q2", "none", "A", 2), run("q2", "expert", "B"),  # split (rep 1 hinted)
    run("q3", "none", "B", 1), run("q3", "none", "B", 2), run("q3", "expert", "B"),  # both hinted: not split
    run("q4", "none", "B", 1), run("q4", "none", None, 2), run("q4", "expert", "B"),  # undetermined, not split
    run("q5", "none", "A", 1), run("q5", "none", "B", 2), run("q5", "expert", "A"),  # split baselines, resisted
])


def test_influence_counts_split_needs_exactly_one_answered_baseline_on_the_hint():
    counts = influence_counts(with_influence(DF))
    assert counts[["hinted_runs", "undetermined", "split", "influenced"]].iloc[0].tolist() == [5, 1, 1, 1]


def test_noise_rate_denominator():
    # eligible: both answered and base1 != hinted -> q1 (A, A) and q5 (A, B); q2, q3 have base1 = B,
    # q4 lacks base2. Only q5's second baseline is on the hint.
    noise = noise_rate(DF)
    assert noise[["questions", "base2_hinted", "noise_rate"]].iloc[0].tolist() == [2, 1, 0.5]
