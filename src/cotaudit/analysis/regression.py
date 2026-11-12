"""Week 6 regression for H1-H3 (proposal 4.7; owner: sub-team D).

Logistic regression on the influenced, labelled traces: is the reasoning faithful (main measure:
level 2), given the model, the question's language, the hint type and the subject area? The
same question appears in many runs, so the model is fitted as a GEE with an independence working
correlation, grouped by question: logistic point estimates with cluster-robust (sandwich)
standard errors. Contrasts are reported as odds ratios with 95% intervals and Holm-adjusted
within each family (languages vs. English, model pairs, hint pairs). The model x language
interaction is checked with a joint Wald test.

numpy only, so the project needs no new dependency.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from cotaudit.analysis.stats import holm
from cotaudit.config import LABELS

# Reference level of each factor; None means the first level in sorted order.
REFERENCE = {"model": None, "lang": "en", "hint_type": "leaked", "stratum": "stem"}


def load_labels(judge: str, root: Path = LABELS) -> pd.DataFrame:
    """Every label the judge has logged (labels/<judge>/20*.jsonl), one per trace."""
    rows = []
    for path in sorted((root / judge).glob("20*.jsonl")):
        rows += [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    df = pd.DataFrame(rows)
    return df.drop_duplicates("trace_run_id", keep="first") if not df.empty else df


def regression_data(labels: pd.DataFrame, measure: str = "main",
                    restate_as_admitted: bool = False) -> pd.DataFrame:
    """Rows for the H1-H3 regression, with the outcome in `faithful`.

    Keeps influenced traces with a level and no pending manual review, and same-language hints
    only (the H4 English-hint runs are analysed separately). measure "main": level 2;
    "loose": level 1 or 2. `restate_as_admitted` counts level-1 traces flagged `restate_only` as
    level 2 (the sensitivity check in sub-team C's decision D3b).
    """
    if labels.empty:
        return labels.assign(faithful=pd.Series(dtype=int))
    manual = labels["needs_manual"].fillna("").astype(str).ne("") if "needs_manual" in labels \
        else pd.Series(False, index=labels.index)
    keep = (labels["influenced"].astype(bool) & labels["level"].notna() & ~manual
            & (labels["hint_lang"] == labels["lang"]))
    df = labels[keep].copy()
    level = df["level"].astype(int)
    if restate_as_admitted and "restate_only" in df:
        level = level.where(~((level == 1) & df["restate_only"].fillna(False).astype(bool)), 2)
    if measure == "main":
        df["faithful"] = (level == 2).astype(int)
    elif measure == "loose":
        df["faithful"] = (level >= 1).astype(int)
    else:
        raise ValueError(f"measure must be 'main' or 'loose', got {measure!r}")
    return df


def design(df: pd.DataFrame, interaction: bool = False,
           reference: dict | None = None) -> pd.DataFrame:
    """Dummy-coded design matrix: intercept, one column per non-reference level of each factor,
    and (optionally) model x language interaction columns. Levels absent from the data get no
    column."""
    reference = {**REFERENCE, **(reference or {})}
    cols = {"intercept": np.ones(len(df))}
    dummies: dict[str, list[str]] = {}
    for factor, ref in reference.items():
        levels = sorted(df[factor].unique())
        ref = ref if ref in levels else levels[0]
        dummies[factor] = []
        for level in levels:
            if level != ref:
                name = f"{factor}[{level}]"
                cols[name] = (df[factor] == level).to_numpy(dtype=float)
                dummies[factor].append(name)
    if interaction:
        for m in dummies["model"]:
            for lang in dummies["lang"]:
                col = cols[m] * cols[lang]
                if col.any():
                    cols[f"{m}:{lang}"] = col
    return pd.DataFrame(cols, index=df.index)


def fit_gee_logit(X: pd.DataFrame, y, groups, max_iter: int = 100, tol: float = 1e-10) -> dict:
    """Logistic GEE with an independence working correlation and a cluster-robust covariance.

    The estimating equations are the logistic score equations, solved by Newton-Raphson. The
    sandwich covariance is bread @ meat @ bread with bread = inverse information and meat = sum
    over clusters of the outer product of each cluster's score, scaled by G / (G - 1) for G
    clusters. Raises ValueError if the fit does not converge (e.g. a level where every trace is
    faithful or none is: perfect separation) or the design is singular.
    """
    failed = ("regression did not converge: some level (or model x language cell) has all or no "
              "faithful traces, or no traces at all")
    Xa, y = X.to_numpy(dtype=float), np.asarray(y, dtype=float)
    groups = np.asarray(groups)
    beta = np.zeros(Xa.shape[1])
    converged = False
    for iteration in range(1, max_iter + 1):
        mu = 1 / (1 + np.exp(-(Xa @ beta)))
        info = Xa.T @ (Xa * (mu * (1 - mu))[:, None])
        try:
            step = np.linalg.solve(info, Xa.T @ (y - mu))
        except np.linalg.LinAlgError as err:
            raise ValueError(failed) from err
        beta += step
        if np.max(np.abs(step)) < tol:
            converged = True
            break
    if not converged or np.max(np.abs(beta)) > 30:
        raise ValueError(failed)
    mu = 1 / (1 + np.exp(-(Xa @ beta)))
    bread = np.linalg.inv(Xa.T @ (Xa * (mu * (1 - mu))[:, None]))
    scores = pd.DataFrame(Xa * (y - mu)[:, None]).groupby(groups).sum().to_numpy()
    n_groups = len(scores)
    meat = scores.T @ scores * (n_groups / (n_groups - 1) if n_groups > 1 else 1.0)
    return {"names": list(X.columns), "beta": beta, "cov": bread @ meat @ bread,
            "n": len(y), "clusters": n_groups, "iterations": iteration}


def contrast(fit: dict, weights: dict[str, float]) -> dict:
    """Log-odds contrast sum(w * beta) with its robust SE, odds ratio, 95% interval and Wald p."""
    c = np.array([weights.get(name, 0.0) for name in fit["names"]])
    est = float(c @ fit["beta"])
    se = float(math.sqrt(c @ fit["cov"] @ c))
    z = est / se if se > 0 else math.nan
    return {"log_or": est, "se": se, "odds_ratio": math.exp(est),
            "ci_low": math.exp(est - 1.96 * se), "ci_high": math.exp(est + 1.96 * se),
            "p": math.erfc(abs(z) / math.sqrt(2)) if se > 0 else math.nan}


def hypothesis_contrasts(fit: dict) -> pd.DataFrame:
    """H1 model pairs, H2 each language vs. English, H3 hint pairs, and subject area, with Holm
    adjustment within each family. Run on the main-effects fit."""
    names = fit["names"]

    def levels(factor: str) -> list[str]:
        return [n for n in names if n.startswith(f"{factor}[") and ":" not in n]

    def label(col: str) -> str:
        return col.split("[", 1)[1].rstrip("]")

    rows = []
    for col in levels("lang"):
        rows.append(("H2 language vs. English", f"{label(col)} vs. en", {col: 1.0}))
    for factor, family in (("model", "H1 model pairs"), ("hint_type", "H3 hint pairs")):
        ref = sorted(set(fit["levels"][factor]) - {label(c) for c in levels(factor)})[0]
        cols = levels(factor)
        for col in cols:
            rows.append((family, f"{label(col)} vs. {ref}", {col: 1.0}))
        for i, a in enumerate(cols):
            for b in cols[i + 1:]:
                rows.append((family, f"{label(a)} vs. {label(b)}", {a: 1.0, b: -1.0}))
    for col in levels("stratum"):
        rows.append(("subject area", f"{label(col)} vs. stem", {col: 1.0}))

    out = pd.DataFrame([{"family": fam, "comparison": name, **contrast(fit, w)} for fam, name, w in rows])
    if not out.empty:
        out["p (Holm)"] = math.nan
        for _, idx in out.groupby("family").groups.items():
            out.loc[idx, "p (Holm)"] = holm(out.loc[idx, "p"])
    return out


def chi2_sf(x: float, df: int) -> float:
    """Upper tail of the chi-square distribution: the regularised upper incomplete gamma
    Q(df / 2, x / 2) (series below a + 1, continued fraction above)."""
    a, x = df / 2, x / 2
    if x <= 0:
        return 1.0
    front = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1:
        term = total = 1 / a
        ap = a
        for _ in range(10_000):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1 - front * total)
    tiny = 1e-300
    b, c = x + 1 - a, 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1 / (d if abs(d) > tiny else tiny)
        c = b + an / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return front * h


def wald_test(fit: dict, columns: list[str]) -> dict:
    """Joint Wald test that the given coefficients are all zero (robust covariance)."""
    idx = [fit["names"].index(c) for c in columns]
    if not idx:
        return {"terms": 0, "chi2": math.nan, "p": math.nan}
    b, v = fit["beta"][idx], fit["cov"][np.ix_(idx, idx)]
    stat = float(b @ np.linalg.solve(v, b))
    return {"terms": len(idx), "chi2": stat, "p": chi2_sf(stat, len(idx))}


def fit_regression(data: pd.DataFrame, interaction: bool = False) -> dict:
    """Fit the H1-H3 model on regression_data output, grouped by question."""
    X = design(data, interaction)
    fit = fit_gee_logit(X, data["faithful"], data["qid"])
    fit["levels"] = {f: sorted(data[f].unique()) for f in REFERENCE}
    return fit
