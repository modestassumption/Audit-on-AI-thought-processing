import pandas as pd

from cotaudit.analysis.influence import wilson, with_influence


def run(qid, hint_type, answer, rep=1, hint_lang="en", lang="en", hinted="B"):
    return {"model": "m", "qid": qid, "lang": lang, "hint_type": hint_type, "rep": rep,
            "hint_lang": None if hint_type == "none" else hint_lang, "answer": answer, "hinted": hinted}


def test_influence_needs_both_baselines_to_avoid_the_hinted_option():
    df = pd.DataFrame([
        run("q1", "none", "A", 1), run("q1", "none", "A", 2), run("q1", "expert", "B"),   # influenced
        run("q2", "none", "A", 1), run("q2", "none", "B", 2), run("q2", "expert", "B"),   # chance
        run("q3", "none", "A", 1), run("q3", "none", None, 2), run("q3", "expert", "B"),  # undetermined
        run("q4", "none", "A", 1), run("q4", "none", "A", 2), run("q4", "expert", "A"),   # resisted
    ])
    h = with_influence(df).set_index("qid")
    assert h["influenced"].to_dict() == {"q1": True, "q2": False, "q3": False, "q4": False}
    assert h["undetermined"].to_dict() == {"q1": False, "q2": False, "q3": True, "q4": False}
    assert h.loc["q3", "influenced_rep1"]


def test_wilson_interval():
    lo, hi = wilson(50, 100)
    assert 0.40 < lo < 0.41 and 0.59 < hi < 0.60
    assert wilson(0, 10)[0] == 0.0
