"""H4 (exploratory): is an English hint inside a Hindi, Chinese or Malayalam question admitted
at a different rate from the same hint in the question's own language? (proposal 4.5 and 4.7;
owner: sub-team D)

The H4 runs use the expert-opinion hint only, so both tests compare, per model and question
language, the expert hint in English with the expert hint in the question's language:

- `h4_influence`: does the English hint change answers as often? Exact McNemar test on the
  questions where both runs are determined (each question gives one pair).
- `h4_faithfulness`: among the influenced traces, is the English hint admitted (level 2, or any
  mention with the loose measure) as often? Two-proportion z-test, as the proposal specifies.

p-values are Holm-adjusted over the model x language cells of each test.
"""

from __future__ import annotations

import math

import pandas as pd

from cotaudit.analysis.stats import holm, mcnemar

H4_HINT = "expert"


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> dict:
    """Pooled two-sided z-test of k1/n1 vs. k2/n2, with the difference and its 95% Wald
    interval (unpooled SE)."""
    if n1 == 0 or n2 == 0:
        return {"diff": math.nan, "diff low": math.nan, "diff high": math.nan, "z": math.nan, "p": math.nan}
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = (p1 - p2) / se0 if se0 > 0 else math.nan
    return {"diff": p1 - p2, "diff low": p1 - p2 - 1.96 * se, "diff high": p1 - p2 + 1.96 * se,
            "z": z, "p": math.erfc(abs(z) / math.sqrt(2)) if se0 > 0 else (1.0 if p1 == p2 else math.nan)}


def _h4_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Expert-hint rows in non-English questions, tagged English hint vs. own-language hint."""
    rows = df[(df["hint_type"] == H4_HINT) & (df["lang"] != "en")
              & ((df["hint_lang"] == "en") | (df["hint_lang"] == df["lang"]))]
    return rows.assign(english_hint=rows["hint_lang"] == "en")


def h4_influence(hinted: pd.DataFrame) -> pd.DataFrame:
    """Per model x question language: influence with the English vs. the own-language expert
    hint, paired by question (both runs determined), exact McNemar test."""
    rows = _h4_rows(hinted[~hinted["undetermined"]])
    cols = ["model", "lang", "pairs", "influenced (en hint)", "influenced (own-language hint)",
            "only en hint", "only own-language hint", "p"]
    out = []
    for (model, lang), g in rows.groupby(["model", "lang"]):
        wide = g.pivot_table(index="qid", columns="english_hint", values="influenced", aggfunc="first")
        if True not in wide or False not in wide:
            continue
        wide = wide.dropna()
        en, own = wide[True].astype(bool), wide[False].astype(bool)
        b, c = int((en & ~own).sum()), int((own & ~en).sum())
        out.append({"model": model, "lang": lang, "pairs": len(wide), "influenced (en hint)": int(en.sum()),
                    "influenced (own-language hint)": int(own.sum()), "only en hint": b,
                    "only own-language hint": c, "p": mcnemar(b, c)})
    out = pd.DataFrame(out, columns=cols)
    out["p (Holm)"] = holm(out["p"])
    return out


def h4_faithfulness(labels: pd.DataFrame) -> pd.DataFrame:
    """Per model x question language: share of influenced traces that admit the hint (column
    `faithful`, from regression.usable_labels), English vs. own-language expert hint,
    two-proportion z-test. diff = English minus own language."""
    rows = _h4_rows(labels) if not labels.empty else labels
    cols = ["model", "lang", "en hint: faithful", "en hint: traces", "own-language hint: faithful",
            "own-language hint: traces", "diff", "diff low", "diff high", "z", "p"]
    out = []
    if not rows.empty:
        for (model, lang), g in rows.groupby(["model", "lang"]):
            en, own = g[g["english_hint"]]["faithful"], g[~g["english_hint"]]["faithful"]
            k1, n1, k2, n2 = int(en.sum()), len(en), int(own.sum()), len(own)
            out.append({"model": model, "lang": lang, "en hint: faithful": k1, "en hint: traces": n1,
                        "own-language hint: faithful": k2, "own-language hint: traces": n2,
                        **two_proportion_z(k1, n1, k2, n2)})
    out = pd.DataFrame(out, columns=cols)
    out["p (Holm)"] = holm(out["p"])
    return out
