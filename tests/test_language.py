import numpy as np
import pandas as pd
import pytest

from cotaudit.analysis.language import (add_reasoning_language, faithfulness_by_switch, reasoning_language,
                                        reasoning_language_table, subject_rates, switch_odds_ratio)

TEXT = {
    "en": "The professor suggests option B, but checking the definition gives C.",
    "hi": "प्रोफ़ेसर विकल्प B बताते हैं, लेकिन परिभाषा जाँचने पर उत्तर C है।",
    "zh": "教授认为答案是B，但根据定义检查后答案是C。",
    "ml": "പ്രൊഫസർ ഓപ്ഷൻ B എന്ന് പറയുന്നു, പക്ഷേ നിർവചനം പരിശോധിച്ചാൽ ഉത്തരം C ആണ്.",
}


def test_each_script_is_recognised():
    for lang, text in TEXT.items():
        assert reasoning_language(text) == lang, lang


def test_option_letters_and_empty_text_do_not_count():
    assert reasoning_language("A B C D x = 2y") is None
    assert reasoning_language("") is None and reasoning_language(None) is None
    assert reasoning_language("उत्तर (B) है") == "hi"           # the single Latin letter is ignored


def test_half_and_half_is_mixed():
    text = "the answer is clearly option " + "उत्तर स्पष्ट रूप से विकल्प है"
    assert reasoning_language(text) == "mixed"
    assert reasoning_language(text, threshold=0.5) in ("en", "hi")


def run(qid, lang, reasoning, model="m"):
    return {"model": model, "qid": qid, "lang": lang, "reasoning": reasoning}


def test_table_counts_reasoning_languages_per_question_language():
    runs = pd.DataFrame([run("q1", "ml", TEXT["en"]), run("q1", "ml", TEXT["en"]), run("q2", "ml", TEXT["ml"]),
                         run("q3", "ml", None), run("q1", "en", TEXT["en"])])
    t = add_reasoning_language(runs)
    assert t["in_question_lang"].tolist() == [False, False, True, False, True]
    table = reasoning_language_table(t).set_index("lang")
    assert table.loc["ml", "traces"] == 3 and table.loc["ml", "in en"] == 2 and table.loc["ml", "in ml"] == 1
    assert table.loc["ml", "own language"] == pytest.approx(1 / 3)
    assert table.loc["en", "own language"] == 1.0


def simulated(n_questions=1500, seed=4):
    """Labelled traces in hi/zh/ml questions; switching to English lowers the log-odds of being
    faithful by 0.7, and models switch at different rates."""
    rng = np.random.default_rng(seed)
    rows = []
    for q in range(n_questions):
        for model, p_switch in (("m1", 0.3), ("m2", 0.7)):
            for lang in ("hi", "zh", "ml"):
                switched = rng.random() < p_switch
                eta = 0.2 + (0.4 if model == "m2" else 0) - (0.7 if switched else 0)
                rows.append({"model": model, "qid": f"q{q}", "lang": lang, "hint_type": "expert",
                             "stratum": "stem" if q % 2 else "humanities",
                             "reasoning_lang": "en" if switched else lang, "in_question_lang": not switched,
                             "faithful": int(rng.random() < 1 / (1 + np.exp(-eta)))})
    return pd.DataFrame(rows)


def test_switching_effect_is_found_per_cell_and_adjusted():
    data = simulated()
    t = faithfulness_by_switch(data)
    assert len(t) == 6 and (t["diff"] > 0).all()               # staying in the language is more faithful
    r = switch_odds_ratio(data)
    assert r["odds_ratio"] == pytest.approx(np.exp(-0.7), rel=0.15)
    assert r["ci_low"] < np.exp(-0.7) < r["ci_high"] and r["p"] < 0.001


def test_switch_analysis_ignores_english_questions():
    data = pd.concat([simulated(200), simulated(200).assign(lang="en")], ignore_index=True)
    assert set(faithfulness_by_switch(data)["lang"]) == {"hi", "zh", "ml"}


def test_subject_rates_resample_questions():
    df = pd.DataFrame({"model": "m", "subject_category": ["STEM"] * 40 + ["Humanities"] * 40,
                       "qid": [f"q{i // 4}" for i in range(80)], "y": ([1, 1, 1, 1] + [0, 0, 0, 0]) * 10})
    t = subject_rates(df, "y").set_index("subject_category")
    assert t.loc["STEM", "questions"] == 10 and t.loc["STEM", "n"] == 40 and t.loc["STEM", "rate"] == 0.5
    stem = t.loc["STEM"]
    # four runs per question all agree, so the question bootstrap is wider than the Wilson interval
    assert stem["bootstrap high"] - stem["bootstrap low"] > stem["wilson high"] - stem["wilson low"]
