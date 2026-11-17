"""Sample-size check (proposal 4.7): the planning table, and the pilot rule on the runs logged so far.

    uv run python scripts/sample_size.py                          # every model in runs/
    uv run python scripts/sample_size.py --rate 0.20 --questions 250 300 450
    uv run python scripts/sample_size.py --root runs/smoke        # try it on the smoke-test logs

Part 1 is the proposal's table (smallest detectable difference in faithfulness at 80% power,
faithfulness near 50%) for the assumed influence rate. Part 2 measures each model's influence
rate from the logged runs and applies the rule: below 15%, raise that model to 450 questions.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.power import pilot_check, planning_table
from cotaudit.config import RUNS


def pct(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:.1f}%"


def points(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:.1f} points"


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def planning_section(rate: float, sizes: list[int]) -> str:
    rows = []
    for questions in sizes:
        for r in planning_table(rate, questions).to_dict("records"):
            detectable = (points(r["detectable difference"]) if pd.notna(r["detectable difference"])
                          else f"+/-{points(r['ci half-width'])} (95% CI, descriptive)")
            rows.append({
                "questions": questions, "comparison": r["comparison"],
                "influenced runs per group": f"{r['influenced per group']:.0f}",
                "alpha split over": "-" if pd.isna(r["alpha split over"]) else int(r["alpha split over"]),
                "smallest detectable difference": detectable,
            })
    return md_table(pd.DataFrame(rows))


def pilot_section(root: Path, models: list[str] | None) -> str:
    df = load_runs(root, models)
    if df.empty:
        return f"No runs logged under {root} yet."
    t = pilot_check(with_influence(df))
    if t.empty:
        return "No hinted runs logged yet."
    shown = pd.DataFrame({
        "model": t["model"],
        "questions so far": t["questions so far"],
        "determined hinted runs": t["determined"],
        "influenced": t["influenced"],
        "influence rate (95% CI)": [f"{pct(r)} ({pct(lo)}-{pct(hi)})"
                                    for r, lo, hi in zip(t["influence rate"], t["ci low"], t["ci high"])],
        "questions needed": t["questions needed"],
        "influenced per language (projected)": t["influenced per language (projected)"].map(
            lambda x: "-" if pd.isna(x) else f"{x:.0f}"),
        "detectable difference within the model": t["detectable difference within the model"].map(points),
        "note": t["note"],
    })
    return md_table(shown)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rate", type=float, default=0.25, help="assumed influence rate (proposal: 0.25)")
    ap.add_argument("--questions", type=int, nargs="+", default=[250, 300, 450],
                    help="question counts to plan for (300 planned, 250 fallback, 450 below 15%% influence)")
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    sections = [
        "# Sample-size check",
        f"## Planning table (influence {args.rate:.0%}, faithfulness near 50%, 80% power)\n\n"
        + planning_section(args.rate, args.questions),
        f"## Pilot rule on the logged runs ({args.root})\n\nSame-language hints, determined runs only. "
        "A model below 15% influence is raised to 450 questions.\n\n" + pilot_section(args.root, args.models),
    ]
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
