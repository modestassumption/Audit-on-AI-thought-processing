"""Week 7 (proposal 4.7; owner: sub-team D): reasoning language and subject area.

    uv run python scripts/language_subject.py --out results/language_subject.md
    uv run python scripts/language_subject.py --area stratum          # STEM vs. humanities only
    uv run python scripts/language_subject.py --root runs/smoke       # try it on the smoke-test logs

1. Which language does each model reason in, per question language? (script of the reasoning)
2. In Hindi, Chinese and Malayalam questions, are traces that switch away from the question's
   language admitted at a different rate? Per-cell z-tests (Holm) and one adjusted GEE odds ratio.
3. Influence and faithfulness per model x subject area, with Wilson and question-bootstrap
   intervals. Subject area: STEM / Social Sciences / Humanities (data/questions.jsonl), or
   --area stratum for the regression's STEM vs. humanities split.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.language import (add_reasoning_language, faithfulness_by_switch, reasoning_language_table,
                                        subject_rates, switch_odds_ratio)
from cotaudit.analysis.regression import load_labels, usable_labels
from cotaudit.config import DATA, LABELS, RUNS, load_experiment
from report_stats import interval, md_table, pct, pval

AREA = {"category": "subject_category", "stratum": "stratum"}


def share(k: int, n: int) -> str:
    return f"{k}/{n} ({pct(k / n)})" if n else "0/0"


def points(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:+.1f}"


def add_category(df: pd.DataFrame) -> pd.DataFrame:
    """Subject category of each question, from data/questions.jsonl."""
    path = DATA / "questions.jsonl"
    rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    cat = {r["qid"]: r.get("subject_category") for r in rows}
    return df.assign(subject_category=df["qid"].map(cat).fillna("unknown"))


def language_section(runs: pd.DataFrame, n_boot: int, seed: int) -> str:
    t = reasoning_language_table(runs, n_boot, seed)
    if t.empty:
        return "No runs with reasoning yet."
    t["own language"] = t["own language"].map(pct)
    t["95% bootstrap (questions)"] = [interval(lo, hi) for lo, hi in zip(t["bootstrap low"], t["bootstrap high"])]
    return md_table(t.drop(columns=["bootstrap low", "bootstrap high"]))


def switch_section(data: pd.DataFrame) -> str:
    t = faithfulness_by_switch(data)
    if t.empty:
        return "No labelled traces from Hindi, Chinese or Malayalam questions yet."
    shown = t[["model", "lang"]].copy()
    shown["stayed in question language"] = [share(k, n) for k, n in zip(t["stayed: faithful"], t["stayed: traces"])]
    shown["switched"] = [share(k, n) for k, n in zip(t["switched: faithful"], t["switched: traces"])]
    shown["difference, points (stayed - switched)"] = t["diff"].map(points)
    shown["95% CI, points"] = [f"{points(lo)} to {points(hi)}" if not pd.isna(lo) else "-"
                               for lo, hi in zip(t["diff low"], t["diff high"])]
    shown["p"], shown["p (Holm)"] = t["p"].map(pval), t["p (Holm)"].map(pval)
    try:
        r = switch_odds_ratio(data)
        adjusted = (f"Adjusted for model, language, hint type and subject area (GEE, grouped by question; "
                    f"{r['traces']} traces, {r['switched']} switched, {r['questions']} questions): odds ratio of "
                    f"being faithful when the reasoning switches = {r['odds_ratio']:.2f} "
                    f"(95% CI {r['ci_low']:.2f}-{r['ci_high']:.2f}), p = {pval(r['p'])}.")
    except (ValueError, KeyError) as err:
        adjusted = f"Adjusted odds ratio not fitted: {err}."
    return md_table(shown) + "\n\n" + adjusted


def subject_section(df: pd.DataFrame, outcome: str, area: str, count_name: str, n_boot: int, seed: int) -> str:
    t = subject_rates(df, outcome, area, n_boot, seed)
    shown = t[["model", area, "questions"]].copy()
    shown[count_name], shown["n"] = t["k"], t["n"]
    shown["rate"] = t["rate"].map(pct)
    shown["95% Wilson"] = [interval(lo, hi) for lo, hi in zip(t["wilson low"], t["wilson high"])]
    shown["95% bootstrap (questions)"] = [interval(lo, hi) for lo, hi in zip(t["bootstrap low"], t["bootstrap high"])]
    return md_table(shown)


def main() -> None:
    cfg = load_experiment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--judge", default=next(iter(cfg["judges"])), help="judge whose labels to use")
    ap.add_argument("--labels-root", type=Path, default=LABELS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--measure", choices=["main", "loose"], default="main")
    ap.add_argument("--area", choices=list(AREA), default="category", help="subject grouping")
    ap.add_argument("--threshold", type=float, default=0.6,
                    help="share of words one script needs for the trace to count as that language")
    ap.add_argument("--n-boot", type=int, default=2000, help="bootstrap resamples of questions")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    runs = load_runs(args.root, args.models) if args.root.is_dir() else pd.DataFrame()
    labels = load_labels(args.judge, args.labels_root)
    if not labels.empty and args.models:
        labels = labels[labels["model"].isin(args.models)]
    if runs.empty and labels.empty:
        raise SystemExit(f"No runs under {args.root} and no labels from {args.judge} yet")

    seed, area = cfg["seed"], AREA[args.area]
    outcome = "level 2" if args.measure == "main" else "level 1 or 2"
    sections = ["# Reasoning language and subject area"]

    if runs.empty:
        sections.append("## Reasoning language\n\nNo runs yet.")
        traced = runs
    else:
        traced = add_category(add_reasoning_language(runs, args.threshold))
        sections.append(f"## Which language is the reasoning in? (all runs with reasoning; a trace counts as one "
                        f"language when {args.threshold:.0%} of its words are in that script, otherwise mixed)\n\n"
                        + language_section(traced, args.n_boot, seed))

    data = usable_labels(labels, args.measure)
    if not data.empty:
        data = add_category(data[data["hint_lang"] == data["lang"]])
    if not data.empty and not traced.empty:
        reasoning = traced.set_index("run_id")[["reasoning_lang", "in_question_lang"]]
        joined = data.join(reasoning, on="trace_run_id", how="inner")
        sections.append(f"## Is the hint admitted less often when the reasoning switches language? "
                        f"(judge {args.judge}; faithful = {outcome}; same-language hints)\n\n" + switch_section(joined))
    else:
        sections.append("## Is the hint admitted less often when the reasoning switches language?\n\n"
                        "Needs both runs and labels.")

    if traced.empty:
        sections.append("## Influence per subject area\n\nNo runs yet.")
    else:
        hinted = add_category(with_influence(runs))
        det = hinted[~hinted["undetermined"] & (hinted["hint_lang"] == hinted["lang"])]
        sections.append("## Influence per subject area (determined runs, same-language hints)\n\n"
                        + (subject_section(det.assign(influenced=det["influenced"].astype(int)), "influenced",
                                           area, "influenced", args.n_boot, seed) if not det.empty else "None yet."))
    sections.append(f"## Faithfulness per subject area (judge {args.judge}; faithful = {outcome})\n\n"
                    + (subject_section(data, "faithful", area, "faithful", args.n_boot, seed)
                       if not data.empty else "No usable labels yet."))

    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
