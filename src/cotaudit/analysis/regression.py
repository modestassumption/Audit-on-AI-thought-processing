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
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from cotaudit.analysis.influence import current_items, current_labels
from cotaudit.analysis.stats import holm
from cotaudit.config import LABELS

# Reference level of each factor; None means the first level in sorted order.
REFERENCE = {"model": None, "lang": "en", "hint_type": "leaked", "stratum": "stem"}


def load_labels(judge: str, root: Path = LABELS, runs: pd.DataFrame | None = None) -> pd.DataFrame:
    """Every label the judge has logged (labels/<judge>/20*.jsonl), one per trace.

    Given `runs` (from load_runs), only labels still current for those runs are kept
    (cotaudit.analysis.influence.current_labels): none on dropped questions or stale traces.
    """
    rows = []
    for path in sorted((root / judge).glob("20*.jsonl")):
        rows += [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if runs is not None:
        rows = current_labels(rows, runs)
    df = pd.DataFrame(rows)
    return df.drop_duplicates("trace_run_id", keep="first") if not df.empty else df


TRACE_COLUMNS = ("model", "qid", "subject", "stratum", "lang", "hint_type", "hint_lang", "condition", "hinted",
                 "gold")


def load_human_labels(name: str, root: Path = LABELS, runs: pd.DataFrame | None = None,
                      rater: str = "adjudicated") -> pd.DataFrame:
    """Human labels from labels/human/<name>/<rater>.csv in the shape of judge labels, for the
    "human labels only" robustness check (proposal 4.7).

    `rater` is a labeller's sheet, or "adjudicated" (default): the settled labels after the third
    member resolves disagreements. key.csv maps each item to its run. `runs` (from load_runs) is
    required: only items whose run is still current, with the reasoning the labellers saw, are
    kept (cotaudit.analysis.influence.current_items), the same rule judge labels follow. The trace
    fields (stratum, subject, ...) then come from the run. Items marked `exclude` or left blank
    get no level and are dropped by usable_labels. Every exported item is an influenced trace. A
    row repeated in the sheet counts once (the first).
    """
    folder = root / "human" / name
    sheet = folder / f"{rater}.csv"
    if not sheet.exists():
        raise FileNotFoundError(f"No human labels at {sheet}")
    current = current_items(folder, runs)
    key = pd.read_csv(folder / "key.csv", dtype=str, encoding="utf-8-sig").drop_duplicates("item_id")
    key = key[key["item_id"].map(current).fillna(False).astype(bool)]
    rated = pd.read_csv(sheet, dtype=str, encoding="utf-8-sig")
    if rated["item_id"].duplicated().any():
        print(f"load_human_labels: {int(rated['item_id'].duplicated().sum())} repeated rows in {sheet.name}; "
              f"the first of each counts", file=sys.stderr)
        rated = rated.drop_duplicates("item_id")
    keep = [c for c in ("item_id", "level", "restate_only") if c in rated]
    df = key.merge(rated[keep], on="item_id", how="inner")
    df["level"] = pd.to_numeric(df["level"], errors="coerce")
    restate = df["restate_only"] if "restate_only" in df else pd.Series("", index=df.index)
    df["restate_only"] = restate.fillna("").str.strip().str.casefold().isin(("yes", "true", "1"))
    # hint type and language from the condition label: "expert" or "expert(en)" (H4)
    parsed = df["condition"].str.extract(r"^(?P<hint_type>[a-z]+)(?:\((?P<hint_lang>[a-z]+)\))?$")
    df["hint_type"] = parsed["hint_type"]
    df["hint_lang"] = parsed["hint_lang"].fillna(df["lang"])
    if runs is not None and not runs.empty:
        cols = [c for c in TRACE_COLUMNS if c in runs]
        from_runs = runs.drop_duplicates("run_id").set_index("run_id")[cols]
        joined = df[["run_id"]].join(from_runs, on="run_id")
        for col in cols:
            df[col] = joined[col].where(joined[col].notna(), df[col] if col in df else None)
    df = df.assign(trace_run_id=df["run_id"], influenced=True, needs_manual=None, labeller=rater)
    return df


def label_source(args, runs: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """(labels, description) for the analysis scripts: the judge's labels, or with --human NAME
    the human labels in labels/human/NAME/<--rater>.csv (proposal 4.7, human labels only)."""
    if getattr(args, "human", None):
        try:
            labels = load_human_labels(args.human, args.labels_root, runs, args.rater)
        except (FileNotFoundError, ValueError) as err:
            raise SystemExit(str(err)) from None
        return labels, f"human labels {args.human}/{args.rater}"
    return load_labels(args.judge, args.labels_root, runs), f"judge {args.judge}"


def add_label_source_args(ap) -> None:
    ap.add_argument("--human", metavar="NAME",
                    help="use human labels from labels/human/NAME/ instead of the judge's (robustness check)")
    ap.add_argument("--rater", default="adjudicated",
                    help="with --human: whose sheet to use (default adjudicated.csv)")


def usable_labels(labels: pd.DataFrame, measure: str = "main",
                  restate_as_admitted: bool = False) -> pd.DataFrame:
    """Influenced traces with a level and no pending manual review, any hint language, with the
    outcome in `faithful`. measure "main": level 2; "loose": level 1 or 2. `restate_as_admitted`
    counts level-1 traces flagged `restate_only` as level 2 (the sensitivity check in sub-team
    C's decision D3b)."""
    if measure not in ("main", "loose"):
        raise ValueError(f"measure must be 'main' or 'loose', got {measure!r}")
    if labels.empty:
        return labels.assign(faithful=pd.Series(dtype=int))
    manual = labels["needs_manual"].fillna("").astype(str).ne("") if "needs_manual" in labels         else pd.Series(False, index=labels.index)
    df = labels[labels["influenced"].astype(bool) & labels["level"].notna() & ~manual].copy()
    level = df["level"].astype(int)
    if restate_as_admitted and "restate_only" in df:
        level = level.where(~((level == 1) & df["restate_only"].fillna(False).astype(bool)), 2)
    df["faithful"] = (level == 2 if measure == "main" else level >= 1).astype(int)
    return df


def regression_data(labels: pd.DataFrame, measure: str = "main",
                    restate_as_admitted: bool = False) -> pd.DataFrame:
    """Rows for the H1-H3 regression: `usable_labels`, same-language hints only (the H4
    English-hint runs are analysed separately, in cotaudit.analysis.h4)."""
    df = usable_labels(labels, measure, restate_as_admitted)
    return df[df["hint_lang"] == df["lang"]] if not df.empty else df


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
