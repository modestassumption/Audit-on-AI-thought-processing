import math

import numpy as np
import pandas as pd
import pytest

from cotaudit.analysis.h4 import h4_faithfulness, h4_influence, two_proportion_z
from cotaudit.analysis.regression import usable_labels
from cotaudit.analysis.stats import beta_binomial_estimates, beta_ppf, betainc, cell_rates, fit_beta_binomial


def test_betainc_matches_closed_forms():
    for x in (0.1, 0.37, 0.8):
        assert betainc(1, 1, x) == pytest.approx(x, rel=1e-12)
        assert betainc(3.5, 1, x) == pytest.approx(x ** 3.5, rel=1e-10)
        assert betainc(1, 4, x) == pytest.approx(1 - (1 - x) ** 4, rel=1e-10)
    assert betainc(7.3, 7.3, 0.5) == pytest.approx(0.5, abs=1e-12)
    assert betainc(2, 3, 0.4) == pytest.approx(0.5248, abs=1e-12)  # 1 - P(Bin(4, 0.4) <= 1)


def test_beta_ppf_inverts_betainc():
    for q in (0.025, 0.5, 0.975):
        assert betainc(12.5, 30.5, beta_ppf(q, 12.5, 30.5)) == pytest.approx(q, abs=1e-12)


def test_fit_recovers_the_prior_of_simulated_cells():
    rng = np.random.default_rng(3)
    p = rng.beta(6, 14, size=300)            # mean 0.3, strength a + b = 20
    n = rng.integers(60, 120, size=300)
    a, b = fit_beta_binomial(rng.binomial(n, p), n)
    assert a / (a + b) == pytest.approx(0.3, abs=0.02)
    assert 12 < a + b < 32


def test_estimates_shrink_towards_the_shared_rate():
    k, n = np.array([5, 40, 20, 22, 18, 25]), np.array([10, 50, 75, 75, 75, 75])
    t = beta_binomial_estimates(k, n)
    shared = k.sum() / n.sum()
    raw = k / n
    assert ((t["bb rate"] - shared).abs() <= np.abs(raw - shared) + 1e-12).all()
    assert (t["bb low"] < t["bb rate"]).all() and (t["bb rate"] < t["bb high"]).all()
    assert t["bb rate"].isna().sum() == 0
    assert beta_binomial_estimates([3], [10])["bb rate"].isna().all()  # one cell: no prior to fit


def test_cell_rates_fits_one_prior_per_model():
    df = pd.DataFrame({"model": ["m1"] * 40 + ["m2"] * 40, "lang": (["en"] * 20 + ["hi"] * 20) * 2,
                       "y": [1] * 10 + [0] * 10 + [1] * 5 + [0] * 15 + [1] * 18 + [0] * 2 + [1] * 16 + [0] * 4})
    t = cell_rates(df, "y", ["model", "lang"]).set_index(["model", "lang"])
    assert t.loc[("m1", "en"), "k"] == 10 and t.loc[("m1", "en"), "n"] == 20
    assert t.loc[("m2", "hi"), "rate"] == 0.8
    assert t.loc[("m1", "hi"), "bb rate"] < 0.6 < t.loc[("m2", "hi"), "bb rate"]  # m2's cells don't pull m1's


def test_two_proportion_z_known_value():
    r = two_proportion_z(30, 100, 50, 100)
    assert r["z"] == pytest.approx(-2.886751, abs=1e-6)       # pooled p 0.4, SE sqrt(0.4*0.6*0.02)
    assert r["p"] == pytest.approx(0.003892, abs=1e-6)
    assert r["diff"] == pytest.approx(-0.2)
    assert math.isnan(two_proportion_z(0, 0, 1, 2)["p"])


def h4_run(qid, hint_lang, influenced, lang="hi", undetermined=False, hint_type="expert"):
    return {"model": "m", "qid": qid, "lang": lang, "hint_type": hint_type, "hint_lang": hint_lang,
            "influenced": influenced, "undetermined": undetermined}


def test_h4_influence_pairs_each_question_once():
    rows = []
    for q in range(12):                      # 9 questions influenced only by the English hint
        rows += [h4_run(q, "en", q < 10), h4_run(q, "hi", q in (0, 10))]
    rows += [h4_run(99, "en", True, undetermined=True), h4_run(99, "hi", False)]   # not a pair
    rows += [h4_run(0, "hi", True, hint_type="leaked"), h4_run(0, "en", True, lang="en")]  # not H4
    t = h4_influence(pd.DataFrame(rows)).iloc[0]
    assert (t["pairs"], t["influenced (en hint)"], t["influenced (own-language hint)"]) == (12, 10, 2)
    assert (t["only en hint"], t["only own-language hint"]) == (9, 1)
    assert t["p"] == pytest.approx(2 * 11 / 2 ** 10)        # exact McNemar, b = 9, c = 1


def test_h4_faithfulness_compares_english_with_own_language_hint():
    def label(hint_lang, level, lang="zh"):
        return {"model": "m", "qid": "q", "lang": lang, "hint_type": "expert", "hint_lang": hint_lang,
                "influenced": True, "level": level, "needs_manual": None}
    labels = pd.DataFrame([label("en", 2)] * 30 + [label("en", 0)] * 70
                          + [label("zh", 2)] * 50 + [label("zh", 1)] * 50 + [label("en", 2, lang="en")] * 5)
    t = h4_faithfulness(usable_labels(labels)).iloc[0]
    assert (t["lang"], t["en hint: traces"], t["own-language hint: traces"]) == ("zh", 100, 100)
    assert t["diff"] == pytest.approx(-0.2) and t["p"] == pytest.approx(0.003892, abs=1e-6)
    loose = h4_faithfulness(usable_labels(labels, "loose")).iloc[0]
    assert loose["own-language hint: faithful"] == 100
