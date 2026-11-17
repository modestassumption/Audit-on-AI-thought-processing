"""H4 (exploratory; proposal 4.7; owner: sub-team D): English hint inside a Hindi, Chinese or
Malayalam question vs. the same expert hint in the question's own language.

    uv run python scripts/h4.py --out results/h4.md
    uv run python scripts/h4.py --measure loose                # admitted = any mention

1. Influence: exact McNemar test per model x language, pairing each question's two runs.
2. Faithfulness: two-proportion z-test per model x language on the influenced, labelled traces.
Both Holm-adjusted over the model x language cells.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.h4 import h4_faithfulness, h4_influence
from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.regression import add_label_source_args, label_source, usable_labels
from cotaudit.config import LABELS, RUNS, load_experiment
from report_stats import md_table, pct, pval


def share(k: int, n: int) -> str:
    return f"{k}/{n} ({pct(k / n)})" if n else "0/0"


def points(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:+.1f}"


def influence_section(runs: pd.DataFrame) -> str:
    t = h4_influence(with_influence(runs)) if not runs.empty else pd.DataFrame()
    if t.empty:
        return "No questions with both an English-hint and an own-language-hint run yet."
    t["p"], t["p (Holm)"] = t["p"].map(pval), t["p (Holm)"].map(pval)
    return md_table(t)


def faithfulness_section(data: pd.DataFrame) -> str:
    t = h4_faithfulness(data)
    if t.empty:
        return "No usable labels for the H4 cells yet."
    shown = t[["model", "lang"]].copy()
    shown["en hint"] = [share(k, n) for k, n in zip(t["en hint: faithful"], t["en hint: traces"])]
    shown["own-language hint"] = [share(k, n) for k, n in
                                  zip(t["own-language hint: faithful"], t["own-language hint: traces"])]
    shown["difference, points (en - own)"] = t["diff"].map(points)
    shown["95% CI, points"] = [f"{points(lo)} to {points(hi)}" if not pd.isna(lo) else "-"
                               for lo, hi in zip(t["diff low"], t["diff high"])]
    shown["p"], shown["p (Holm)"] = t["p"].map(pval), t["p (Holm)"].map(pval)
    return md_table(shown)


def main() -> None:
    cfg = load_experiment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--judge", default=next(iter(cfg["judges"])), help="judge whose labels to use")
    ap.add_argument("--labels-root", type=Path, default=LABELS)
    add_label_source_args(ap)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--measure", choices=["main", "loose"], default="main")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    runs = load_runs(args.root, args.models) if args.root.is_dir() else pd.DataFrame()
    labels, source = label_source(args, runs)
    if not labels.empty and args.models:
        labels = labels[labels["model"].isin(args.models)]
    if runs.empty and labels.empty:
        raise SystemExit(f"No runs under {args.root} and no labels from {source} yet")

    outcome = "level 2" if args.measure == "main" else "level 1 or 2"
    sections = [
        "# H4: English hint vs. own-language hint (expert opinion; hi, zh, ml questions)",
        "## Does the English hint change answers as often? (McNemar, paired by question)\n\n"
        + influence_section(runs),
        f"## Is it admitted as often? ({source}; admitted = {outcome}; two-proportion z-test)\n\n"
        + faithfulness_section(usable_labels(labels, args.measure)),
    ]
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
