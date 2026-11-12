"""Week 6 regression for H1-H3 (proposal 4.7; owner: sub-team D).

    uv run python scripts/regression.py --out results/regression.md
    uv run python scripts/regression.py --measure loose                 # any mention (level 1 or 2)
    uv run python scripts/regression.py --restate-as-admitted          # sub-team C's D3b check

Reads one judge's labels (labels/<judge>/, from scripts/run_judge.py), keeps influenced traces
with a usable level and same-language hints, and fits a logistic GEE grouped by question:
faithful ~ model + language + hint type + subject area. Reports odds ratios with 95% robust
intervals, Holm-adjusted within each family, then refits with the model x language interaction
and tests it jointly.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.regression import (fit_regression, hypothesis_contrasts, load_labels,
                                          regression_data, wald_test)
from cotaudit.config import LABELS, load_experiment


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def pval(p: float) -> str:
    return "-" if pd.isna(p) else ("<0.001" if p < 0.001 else f"{p:.3f}")


def counts_section(data: pd.DataFrame) -> str:
    t = (data.groupby(["model", "lang"])["faithful"].agg(["size", "sum"]).reset_index()
         .rename(columns={"size": "traces", "sum": "faithful"}))
    t["rate"] = (t["faithful"] / t["traces"]).map(lambda x: f"{100 * x:.1f}%")
    return md_table(t)


def contrasts_section(data: pd.DataFrame) -> str:
    try:
        fit = fit_regression(data)
    except ValueError as err:
        return f"Main-effects model not fitted: {err}."
    t = hypothesis_contrasts(fit)
    shown = pd.DataFrame({
        "family": t["family"], "comparison": t["comparison"],
        "odds ratio": t["odds_ratio"].map(lambda x: f"{x:.2f}"),
        "95% CI": [f"{lo:.2f}-{hi:.2f}" for lo, hi in zip(t["ci_low"], t["ci_high"])],
        "p": t["p"].map(pval), "p (Holm)": t["p (Holm)"].map(pval),
    })
    return (f"{fit['n']} traces, {fit['clusters']} questions. Odds ratio > 1: more often faithful "
            "than the comparison level.\n\n" + md_table(shown))


def interaction_section(data: pd.DataFrame) -> str:
    try:
        fit = fit_regression(data, interaction=True)
    except ValueError as err:
        return f"Interaction model not fitted: {err}."
    test = wald_test(fit, [n for n in fit["names"] if ":" in n])
    if not test["terms"]:
        return "Only one model or one language in the data: no interaction to test."
    return (f"Joint Wald test of the {test['terms']} model x language terms: "
            f"chi2 = {test['chi2']:.2f}, p = {pval(test['p'])}.")


def main() -> None:
    cfg = load_experiment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--judge", default=next(iter(cfg["judges"])), help="judge whose labels to use")
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--measure", choices=["main", "loose"], default="main")
    ap.add_argument("--restate-as-admitted", action="store_true",
                    help="count level-1 traces flagged restate_only as level 2")
    ap.add_argument("--labels-root", type=Path, default=LABELS)
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    labels = load_labels(args.judge, args.labels_root)
    if not labels.empty and args.models:
        labels = labels[labels["model"].isin(args.models)]
    data = regression_data(labels, args.measure, args.restate_as_admitted)
    if data.empty:
        raise SystemExit(f"No usable labels from {args.judge} under {args.labels_root / args.judge} yet")

    outcome = "level 2" if args.measure == "main" else "level 1 or 2"
    if args.restate_as_admitted:
        outcome += ", restate-only traces counted as level 2"
    sections = [
        f"# Regression (judge {args.judge}; faithful = {outcome})",
        "## Faithful traces per model and language\n\n" + counts_section(data),
        "## H1-H3: main-effects GEE, grouped by question\n\n" + contrasts_section(data),
        "## Model x language interaction\n\n" + interaction_section(data),
    ]
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
