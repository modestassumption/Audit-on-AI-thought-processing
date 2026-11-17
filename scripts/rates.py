"""Per-cell rates (proposal 4.7, first bullet; owner: sub-team D): influence and faithfulness
per model x language x hint, with 95% Wilson intervals and Beta-Binomial estimates as a check.

    uv run python scripts/rates.py --out results/rates.md
    uv run python scripts/rates.py --measure loose               # faithful = level 1 or 2

Influence comes from the run logs (determined hinted runs, same-language hints); faithfulness
from one judge's labels (influenced traces with a usable level). The Beta-Binomial column fits
one Beta prior per model across its language x hint cells and reports each cell's posterior
mean and 95% interval, so a small cell is pulled towards its model's typical rate.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.regression import load_labels, usable_labels
from cotaudit.analysis.stats import cell_rates
from cotaudit.config import LABELS, RUNS, load_experiment
from report_stats import interval, md_table, pct

CELL = ["model", "lang", "hint"]


def rates_table(df: pd.DataFrame, outcome: str, count_name: str) -> str:
    t = cell_rates(df.assign(hint=df["hint_type"]), outcome, CELL)
    shown = t[CELL].copy()
    shown[count_name], shown["n"] = t["k"], t["n"]
    shown["rate"] = t["rate"].map(pct)
    shown["95% Wilson"] = [interval(lo, hi) for lo, hi in zip(t["wilson low"], t["wilson high"])]
    shown["Beta-Binomial"] = t["bb rate"].map(pct)
    shown["95% Beta-Binomial"] = [interval(lo, hi) for lo, hi in zip(t["bb low"], t["bb high"])]
    return md_table(shown)


def main() -> None:
    cfg = load_experiment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--judge", default=next(iter(cfg["judges"])), help="judge whose labels to use")
    ap.add_argument("--labels-root", type=Path, default=LABELS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--measure", choices=["main", "loose"], default="main")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    runs = load_runs(args.root, args.models) if args.root.is_dir() else pd.DataFrame()
    labels = load_labels(args.judge, args.labels_root, runs)
    if not labels.empty and args.models:
        labels = labels[labels["model"].isin(args.models)]
    if runs.empty and labels.empty:
        raise SystemExit(f"No runs under {args.root} and no labels from {args.judge} yet")

    sections = ["# Rates per model, language and hint"]
    if runs.empty:
        sections.append("## Influence\n\nNo runs yet.")
    else:
        hinted = with_influence(runs)
        det = hinted[~hinted["undetermined"] & (hinted["hint_lang"] == hinted["lang"])]
        det = det.assign(influenced=det["influenced"].astype(int))
        sections.append("## Influence (determined hinted runs, same-language hints)\n\n"
                        + (rates_table(det, "influenced", "influenced") if not det.empty else "None yet."))
    data = usable_labels(labels, args.measure)
    data = data[data["hint_lang"] == data["lang"]] if not data.empty else data
    outcome = "level 2" if args.measure == "main" else "level 1 or 2"
    sections.append(f"## Faithfulness (judge {args.judge}; faithful = {outcome})\n\n"
                    + (rates_table(data, "faithful", "faithful") if not data.empty else "No usable labels yet."))
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
