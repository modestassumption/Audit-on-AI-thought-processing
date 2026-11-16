"""Week 7: reasoning-language and subject-area analysis (proposal 1 and 4.7; owner: sub-team D).

Reasoning language. Models often reason in English or Chinese instead of the question's language
(proposal, motivation). Each trace's reasoning is assigned the language whose script carries most
of its words: Latin -> en, Devanagari -> hi, Han characters -> zh, Malayalam -> ml. Latin words of
one letter (variables, option letters) are ignored, and each Han character counts as one word.
If no script reaches `threshold` of the words, the trace is "mixed". This is a script check, not
a language model: English and other Latin-script languages are not told apart, which is fine for
these four languages.

- `reasoning_language_table`: per model x question language, how many traces reason in each
  language, and the share in the question's own language with a bootstrap interval over questions.
- `faithfulness_by_switch`: in Hindi, Chinese and Malayalam questions, are traces that switch away
  from the question's language admitted at a different rate? Two-proportion z-test per model x
  language (Holm), plus one GEE odds ratio adjusted for model, language, hint type and subject.
  Observational: the model chooses its reasoning language, so this is association, not effect.

Subject area. `subject_rates` gives influence or faithfulness per model x subject area, with
Wilson and question-bootstrap intervals (each question appears in several languages and hints).
"""

from __future__ import annotations

import math
import re

import pandas as pd

from cotaudit.analysis.h4 import two_proportion_z
from cotaudit.analysis.regression import design, fit_gee_logit
from cotaudit.analysis.stats import cluster_bootstrap, holm, rate_intervals

LANGS = ["en", "hi", "zh", "ml"]
_WORDS = {
    "en": re.compile(r"[A-Za-z]{2,}"),
    "hi": re.compile(r"[ऀ-ॿ]+"),
    "zh": re.compile(r"[㐀-䶿一-鿿豈-﫿]"),
    "ml": re.compile(r"[ഀ-ൿ]+"),
}


def script_shares(text: str | None) -> dict[str, float]:
    """Share of the words in `text` written in each of the four scripts (empty if none)."""
    text = text if isinstance(text, str) else ""   # missing reasoning arrives as None or NaN
    counts = {lang: len(rx.findall(text)) for lang, rx in _WORDS.items()}
    total = sum(counts.values())
    return {lang: c / total for lang, c in counts.items()} if total else {}


def reasoning_language(text: str | None, threshold: float = 0.6) -> str | None:
    """'en', 'hi', 'zh', 'ml', 'mixed' (no script reaches the threshold) or None (no words)."""
    shares = script_shares(text)
    if not shares:
        return None
    lang = max(shares, key=shares.get)
    return lang if shares[lang] >= threshold else "mixed"


def add_reasoning_language(df: pd.DataFrame, threshold: float = 0.6) -> pd.DataFrame:
    """Adds `reasoning_lang` and `in_question_lang` (reasoning in the question's language)."""
    lang = df["reasoning"].map(lambda t: reasoning_language(t, threshold)) if not df.empty \
        else pd.Series(dtype=object)
    return df.assign(reasoning_lang=lang, in_question_lang=lang == df["lang"])


def reasoning_language_table(runs: pd.DataFrame, n_boot: int = 2000, seed: int = 21) -> pd.DataFrame:
    """Per model x question language: traces with reasoning, how many reason in each language,
    and the share in the question's language with a 95% bootstrap interval over questions."""
    df = runs[runs["reasoning_lang"].notna()]
    rows = []
    for (model, lang), g in df.groupby(["model", "lang"]):
        counts = g["reasoning_lang"].value_counts()
        per_q = g.groupby("qid")["in_question_lang"].agg(["sum", "count"])
        lo, hi = cluster_bootstrap(per_q["sum"], per_q["count"], n_boot, seed)
        rows.append({"model": model, "lang": lang, "traces": len(g),
                     **{f"in {code}": int(counts.get(code, 0)) for code in LANGS + ["mixed"]},
                     "own language": g["in_question_lang"].mean(), "bootstrap low": lo, "bootstrap high": hi})
    return pd.DataFrame(rows)


def faithfulness_by_switch(data: pd.DataFrame) -> pd.DataFrame:
    """Hindi, Chinese and Malayalam questions: faithful share when the reasoning stays in the
    question's language vs. when it switches (any other language or mixed), per model x language.
    `data` holds labelled traces with `faithful` and `in_question_lang`. diff = stayed - switched."""
    df = data[(data["lang"] != "en") & data["reasoning_lang"].notna()]
    rows = []
    for (model, lang), g in df.groupby(["model", "lang"]):
        stay, switch = g[g["in_question_lang"]]["faithful"], g[~g["in_question_lang"]]["faithful"]
        rows.append({"model": model, "lang": lang, "stayed: faithful": int(stay.sum()), "stayed: traces": len(stay),
                     "switched: faithful": int(switch.sum()), "switched: traces": len(switch),
                     **two_proportion_z(int(stay.sum()), len(stay), int(switch.sum()), len(switch))})
    out = pd.DataFrame(rows, columns=["model", "lang", "stayed: faithful", "stayed: traces", "switched: faithful",
                                      "switched: traces", "diff", "diff low", "diff high", "z", "p"])
    out["p (Holm)"] = holm(out["p"])
    return out


def switch_odds_ratio(data: pd.DataFrame) -> dict:
    """Odds ratio of being faithful for traces that switch away from the question's language,
    adjusted for model, language, hint type and subject area (GEE grouped by question; Hindi,
    Chinese and Malayalam questions only). Raises ValueError if the fit fails."""
    df = data[(data["lang"] != "en") & data["reasoning_lang"].notna()]
    X = design(df, reference={"lang": "hi"})
    X["switched"] = (~df["in_question_lang"]).to_numpy(dtype=float)
    fit = fit_gee_logit(X, df["faithful"], df["qid"])
    i = fit["names"].index("switched")
    est, se = float(fit["beta"][i]), float(math.sqrt(fit["cov"][i, i]))
    return {"traces": fit["n"], "questions": fit["clusters"], "switched": int(X["switched"].sum()),
            "odds_ratio": math.exp(est), "ci_low": math.exp(est - 1.96 * se),
            "ci_high": math.exp(est + 1.96 * se), "p": math.erfc(abs(est / se) / math.sqrt(2))}


def subject_rates(df: pd.DataFrame, outcome: str, area: str = "subject_category",
                  n_boot: int = 2000, seed: int = 21) -> pd.DataFrame:
    """Rate of the 0/1 column `outcome` per model x subject area, with 95% Wilson and
    question-bootstrap intervals."""
    return rate_intervals(df, outcome, ["model", area], n_boot, seed)
