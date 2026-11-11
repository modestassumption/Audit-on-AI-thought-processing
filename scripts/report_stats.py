"""Week 6 statistics (proposal 4.7; owner: sub-team D): do the hints change answers, and how
sure are the influence rates?

    uv run python scripts/report_stats.py --out results/stats.md
    uv run python scripts/report_stats.py --root runs/smoke          # try it on the smoke-test logs

1. McNemar's test per model x language x hint: each hinted run paired with the same question's
   first no-hint run (--baseline-rep 2 for the second), Holm-adjusted over all cells.
2. Influence rates per model and per model x language, same-language hints: 95% Wilson interval
   (runs independent) and 95% bootstrap interval resampling questions (--n-boot; seed from
   configs/experiment.yaml).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.stats import hint_effect, influence_intervals
from cotaudit.config import RUNS, load_experiment


def pct(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:.1f}%"


def interval(lo: float, hi: float) -> str:
    return "-" if pd.isna(lo) or pd.isna(hi) else f"{pct(lo)}-{pct(hi)}"


def pval(p: float) -> str:
    return "-" if pd.isna(p) else ("<0.001" if p < 0.001 else f"{p:.3f}")


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def effect_section(hinted: pd.DataFrame, baseline_rep: int) -> str:
    t = hint_effect(hinted, baseline_rep)
    if t.empty:
        return "No hinted runs with a matching no-hint run yet."
    t["p"] = t["p"].map(pval)
    t["p (Holm)"] = t["p (Holm)"].map(pval)
    return md_table(t)


def interval_section(hinted: pd.DataFrame, by: list[str], n_boot: int, seed: int) -> str:
    t = influence_intervals(hinted[hinted["hint_lang"] == hinted["lang"]], by, n_boot, seed)
    if t.empty:
        return "No determined hinted runs yet."
    shown = t[by + ["questions", "determined", "influenced"]].copy()
    shown["rate"] = t["rate"].map(pct)
    shown["95% Wilson"] = [interval(lo, hi) for lo, hi in zip(t["wilson low"], t["wilson high"])]
    shown["95% bootstrap (questions)"] = [interval(lo, hi) for lo, hi in zip(t["bootstrap low"], t["bootstrap high"])]
    return md_table(shown)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--baseline-rep", type=int, choices=[1, 2], default=1)
    ap.add_argument("--n-boot", type=int, default=2000, help="bootstrap resamples of questions")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    df = load_runs(args.root, args.models)
    if df.empty:
        raise SystemExit(f"No runs found under {args.root}")
    hinted = with_influence(df)
    seed = load_experiment()["seed"]

    sections = [
        "# Statistics report",
        f"## Do the hints change answers? (McNemar vs. no-hint run {args.baseline_rep}, Holm over all cells)\n\n"
        + effect_section(hinted, args.baseline_rep),
        f"## Influence per model (same-language hints; bootstrap: {args.n_boot} resamples of questions)\n\n"
        + interval_section(hinted, ["model"], args.n_boot, seed),
        "## Influence per model and language\n\n" + interval_section(hinted, ["model", "lang"], args.n_boot, seed),
    ]
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
