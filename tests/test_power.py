import pandas as pd

from cotaudit.analysis.influence import with_influence
from cotaudit.analysis.power import min_detectable_difference, pilot_check, planning_table


def test_planning_table_matches_the_proposal():
    # Proposal 4.7 at 25% influence and 300 questions: 675 / 900 / 225 / 75 influenced runs per
    # group, detectable differences of about 9, 8 and 13 points, and an interval of about +/-11.
    t = planning_table(0.25, 300)
    assert t["influenced per group"].round().tolist() == [675, 900, 225, 75]
    assert (100 * t["detectable difference"].dropna()).round().tolist() == [9, 8, 13]
    assert round(100 * t["ci half-width"].dropna().iloc[0]) == 11


def test_detectable_difference_grows_with_more_tests_and_fewer_runs():
    assert min_detectable_difference(225, comparisons=3) > min_detectable_difference(225)
    assert min_detectable_difference(100) > min_detectable_difference(400)
    assert pd.isna(min_detectable_difference(0))


def run(model, qid, hint_type, answer, rep=1):
    return {"model": model, "qid": qid, "lang": "en", "hint_type": hint_type, "rep": rep,
            "hint_lang": None if hint_type == "none" else "en", "answer": answer, "hinted": "B"}


def test_pilot_rule_raises_models_below_15_percent():
    rows = []
    for model, n_influenced in (("low", 1), ("high", 5)):  # 1/10 and 5/10 hinted runs influenced
        for i in range(10):
            rows += [run(model, f"q{i}", "none", "A", 1), run(model, f"q{i}", "none", "A", 2),
                     run(model, f"q{i}", "expert", "B" if i < n_influenced else "A")]
    t = pilot_check(with_influence(pd.DataFrame(rows))).set_index("model")
    assert t.loc["low", "influence rate"] == 0.1 and t.loc["low", "questions needed"] == 450
    assert t.loc["high", "influence rate"] == 0.5 and t.loc["high", "questions needed"] == 300
    assert t.loc["low", "note"]  # 1/10 is too few runs to be sure it is below 15%
