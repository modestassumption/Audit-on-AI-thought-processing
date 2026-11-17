import math

import pandas as pd

from cotaudit.analysis.influence import condition_label, wilson, with_influence
from cotaudit.analysis.stats import cluster_bootstrap, hint_effect, holm, influence_intervals, mcnemar


def test_mcnemar_exact_p_values():
    assert mcnemar(0, 0) == 1.0
    assert mcnemar(10, 0) == 2 / 2 ** 10
    assert round(mcnemar(3, 12), 4) == 0.0352  # 2 * P(X <= 3) for X ~ Binomial(15, 1/2)
    assert mcnemar(3, 12) == mcnemar(12, 3)
    assert mcnemar(5, 5) == 1.0


def test_holm_keeps_input_order_and_skips_nan():
    adjusted = holm([0.01, 0.04, 0.03, 0.005, math.nan])
    assert [round(p, 3) for p in adjusted[:4]] == [0.03, 0.06, 0.06, 0.02]
    assert math.isnan(adjusted[4])


def run(qid, hint_type, answer, rep=1):
    return {"model": "m", "qid": qid, "lang": "en", "hint_type": hint_type, "rep": rep,
            "hint_lang": None if hint_type == "none" else "en", "answer": answer, "hinted": "B"}


def frame(rows):
    """Runs as load_runs returns them, with the condition label."""
    df = pd.DataFrame(rows)
    return df.assign(condition=df.apply(condition_label, axis=1))


def test_hint_effect_counts_discordant_pairs():
    df = frame([
        run("q1", "none", "A", 1), run("q1", "none", "A", 2), run("q1", "expert", "B"),   # only with hint
        run("q2", "none", "B", 1), run("q2", "none", "A", 2), run("q2", "expert", "A"),   # only without (rep 1)
        run("q3", "none", "B", 1), run("q3", "none", "B", 2), run("q3", "expert", "B"),   # both
        run("q4", "none", None, 1), run("q4", "none", "A", 2), run("q4", "expert", "B"),  # rep 1 missing
    ])
    hinted = with_influence(df)
    t = hint_effect(hinted).iloc[0]
    assert (t["pairs"], t["only with hint"], t["only without hint"], t["p"]) == (3, 1, 1, 1.0)
    t2 = hint_effect(hinted, baseline_rep=2).iloc[0]
    assert (t2["pairs"], t2["only with hint"], t2["only without hint"]) == (4, 2, 0)


def test_bootstrap_over_questions_is_wider_when_runs_of_a_question_agree():
    # 30 questions x 10 runs: 9 questions influenced on every run, 21 on none, so 30% overall.
    k, n = [10] * 9 + [0] * 21, [10] * 30
    lo, hi = cluster_bootstrap(k, n, seed=21)
    wlo, whi = wilson(90, 300)
    assert lo < 0.3 < hi
    assert hi - lo > 2 * (whi - wlo)
    assert cluster_bootstrap(k, n, seed=21) == (lo, hi)  # same seed, same interval
    assert all(math.isnan(x) for x in cluster_bootstrap([1], [3]))  # one question: no spread to resample


def test_influence_intervals_pool_runs_by_group():
    rows = []
    for i in range(4):  # q0 and q1 follow both hints, q2 and q3 never do
        rows += [run(f"q{i}", "none", "A", 1), run(f"q{i}", "none", "A", 2)]
        rows += [run(f"q{i}", hint, "B" if i < 2 else "A") for hint in ("expert", "leaked")]
    t = influence_intervals(with_influence(frame(rows)), ["model"], n_boot=200).iloc[0]
    assert (t["questions"], t["determined"], t["influenced"], t["rate"]) == (4, 8, 4, 0.5)
    assert t["bootstrap low"] <= 0.5 <= t["bootstrap high"]
