import math

import numpy as np
import pandas as pd
import pytest

from cotaudit.analysis.regression import (chi2_sf, design, fit_gee_logit, fit_regression,
                                          hypothesis_contrasts, regression_data, wald_test)

TRUE = {"intercept": -0.2, "model[m2]": 0.8, "lang[hi]": -0.6, "hint_type[expert]": -0.5,
        "stratum[humanities]": 0.3}


def simulated(n_questions=4000, seed=1):
    """One trace per question x hint x language, outcome drawn from TRUE."""
    rng = np.random.default_rng(seed)
    rows = []
    for q in range(n_questions):
        model = "m1" if q % 2 else "m2"
        stratum = "stem" if q % 3 else "humanities"
        for lang in ("en", "hi"):
            for hint in ("expert", "leaked"):
                rows.append({"qid": f"q{q}", "model": model, "lang": lang, "hint_type": hint,
                             "stratum": stratum})
    df = pd.DataFrame(rows)
    X = design(df)
    eta = sum(X[c] * b for c, b in TRUE.items())
    df["faithful"] = (rng.random(len(df)) < 1 / (1 + np.exp(-eta))).astype(int)
    return df


def test_chi2_tail_matches_closed_forms():
    assert chi2_sf(3.841458820694124, 1) == pytest.approx(0.05, abs=1e-9)
    assert chi2_sf(1.3, 2) == pytest.approx(math.exp(-0.65), rel=1e-12)            # df 2: exp(-x/2)
    assert chi2_sf(1.0, 4) == pytest.approx(math.exp(-0.5) * 1.5, rel=1e-12)       # series branch
    assert chi2_sf(10.0, 4) == pytest.approx(math.exp(-5) * 6, rel=1e-12)          # continued fraction


def test_fit_recovers_known_coefficients():
    df = simulated()
    fit = fit_regression(df)
    est = dict(zip(fit["names"], fit["beta"]))
    for name, true in TRUE.items():
        assert est[name] == pytest.approx(true, abs=0.12), name


def test_copying_rows_inside_their_question_leaves_robust_errors_unchanged():
    df = simulated(n_questions=400, seed=2)
    once = fit_gee_logit(design(df), df["faithful"], df["qid"])
    twice_df = pd.concat([df, df], ignore_index=True)
    twice = fit_gee_logit(design(twice_df), twice_df["faithful"], twice_df["qid"])
    np.testing.assert_allclose(twice["beta"], once["beta"], rtol=1e-8)
    np.testing.assert_allclose(twice["cov"], once["cov"], rtol=1e-6)  # runs of a question are not new evidence


def test_contrasts_cover_each_hypothesis_with_holm():
    t = hypothesis_contrasts(fit_regression(simulated())).set_index("comparison")
    assert t.loc["hi vs. en", "family"] == "H2 language vs. English"
    assert t.loc["expert vs. leaked", "family"] == "H3 hint pairs"
    assert t.loc["m2 vs. m1", "family"] == "H1 model pairs"
    assert t.loc["hi vs. en", "odds_ratio"] < 1 < t.loc["m2 vs. m1", "odds_ratio"]
    assert (t["p (Holm)"] >= t["p"]).all()


def test_interaction_test_finds_nothing_when_there_is_none():
    test = wald_test(fit := fit_regression(simulated(), interaction=True), [n for n in fit["names"] if ":" in n])
    assert test["terms"] == 1 and test["p"] > 0.01


def label(level, influenced=True, manual=None, lang="en", hint_lang="en", restate=False):
    return {"qid": "q", "model": "m", "lang": lang, "hint_lang": hint_lang, "hint_type": "expert",
            "stratum": "stem", "influenced": influenced, "level": level, "needs_manual": manual,
            "restate_only": restate}


def test_regression_data_keeps_usable_same_language_labels():
    labels = pd.DataFrame([
        label(2), label(1), label(0), label(1, restate=True),
        label(2, influenced=False),                 # not influenced
        label(2, manual="quote_not_found"),         # waiting for manual review
        label(None, manual="unparseable"),          # no level
        label(2, lang="hi", hint_lang="en"),        # H4 run, analysed separately
    ])
    assert regression_data(labels)["faithful"].tolist() == [1, 0, 0, 0]
    assert regression_data(labels, "loose")["faithful"].tolist() == [1, 1, 0, 1]
    assert regression_data(labels, restate_as_admitted=True)["faithful"].tolist() == [1, 0, 0, 1]


def test_perfect_separation_is_reported():
    df = simulated(n_questions=200)
    df["faithful"] = (df["lang"] == "hi").astype(int)
    with pytest.raises(ValueError, match="did not converge"):
        fit_regression(df)
