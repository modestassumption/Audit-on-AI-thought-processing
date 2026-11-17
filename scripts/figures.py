"""Week 7 figures for the report (proposal 4.7; owner: sub-team D), as SVG files.

    uv run python scripts/figures.py                            # writes results/figures/*.svg
    uv run python scripts/figures.py --root runs/smoke          # try it on the smoke-test logs

From the run logs:
  influence.svg            influence rate per model x language, one dot per hint type
                           (determined runs, same-language hints; 95% bootstrap over questions)
  h4_influence.svg         H4: influence with the English vs. the own-language expert hint
  reasoning_language.svg   which language the reasoning is in, per model x question language
From one judge's labels (labels/<judge>/):
  faithfulness.svg         faithful share of influenced traces, per model x language x hint
  h4_faithfulness.svg      H4: faithful share with the English vs. the own-language expert hint
  regression.svg           H1-H3 odds ratios from the GEE regression (log axis, 95% robust CI)

A figure whose data is not there yet is skipped and listed at the end.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.figures import NEUTRAL, SERIES, interval_chart, stacked_bars
from cotaudit.analysis.h4 import h4_rows
from cotaudit.analysis.influence import load_runs, with_influence
from cotaudit.analysis.language import LANGS, add_reasoning_language, reasoning_language_table
from cotaudit.analysis.regression import fit_regression, hypothesis_contrasts, load_labels, usable_labels
from cotaudit.analysis.stats import rate_intervals
from cotaudit.config import LABELS, RUNS, load_experiment

LANG_NAME = {"en": "English", "hi": "Hindi", "zh": "Chinese", "ml": "Malayalam", "mixed": "mixed"}
H4_SERIES = {True: "English hint", False: "own-language hint"}


def order_langs(df: pd.DataFrame) -> pd.DataFrame:
    """Sort rows model, then language in the order en, hi, zh, ml."""
    return df.assign(_l=df["lang"].map({l: i for i, l in enumerate(LANGS)})).sort_values(["model", "_l"])


def rate_rows(t: pd.DataFrame, series_col: str, names: dict | None = None) -> list[dict]:
    t = order_langs(t)
    return [{"row": f"{r['model']} · {LANG_NAME.get(r['lang'], r['lang'])}",
             "series": names[r[series_col]] if names else r[series_col], "value": r["rate"],
             "low": r["bootstrap low"], "high": r["bootstrap high"], "n": int(r["n"])}
            for _, r in t.iterrows()]


def hint_rate_chart(df: pd.DataFrame, outcome: str, hints: list[str], title: str, x_label: str,
                    n_boot: int, seed: int) -> str:
    t = rate_intervals(df, outcome, ["model", "lang", "hint_type"], n_boot, seed)
    series = [h for h in hints if h in set(t["hint_type"])]
    return interval_chart(rate_rows(t, "hint_type"), series, title=title, x_label=x_label)


def h4_chart(df: pd.DataFrame, outcome: str, title: str, x_label: str, n_boot: int, seed: int) -> str | None:
    rows = h4_rows(df)
    if rows.empty or rows["english_hint"].nunique() < 2:
        return None
    t = rate_intervals(rows, outcome, ["model", "lang", "english_hint"], n_boot, seed)
    return interval_chart(rate_rows(t, "english_hint", H4_SERIES), list(H4_SERIES.values()),
                          title=title, x_label=x_label)


def language_chart(runs: pd.DataFrame, threshold: float, n_boot: int, seed: int) -> str | None:
    t = reasoning_language_table(add_reasoning_language(runs, threshold), n_boot, seed)
    if t.empty:
        return None
    t = order_langs(t)
    parts = LANGS + ["mixed"]
    rows = [(f"{r['model']} · {LANG_NAME[r['lang']]} questions",
             {LANG_NAME[p]: int(r[f"in {p}"]) for p in parts}) for _, r in t.iterrows()]
    colors = {LANG_NAME[p]: c for p, c in zip(LANGS, SERIES)} | {"mixed": NEUTRAL}
    return stacked_bars(rows, [LANG_NAME[p] for p in parts], colors=colors,
                        title=f"Language of the reasoning (one script ≥ {threshold:.0%} of words, else mixed)")


def regression_chart(data: pd.DataFrame, outcome: str) -> str | None:
    try:
        t = hypothesis_contrasts(fit_regression(data))
    except ValueError:
        return None
    if t.empty:
        return None
    family = t["family"].map(lambda f: f.split()[0] if f.startswith("H") else "subject")   # "H2", ...
    rows = [{"row": f"{fam} · {r['comparison']}", "series": "odds ratio", "value": r["odds_ratio"],
             "low": r["ci_low"], "high": r["ci_high"]} for fam, (_, r) in zip(family, t.iterrows())]
    lo = min(0.5, float(t["ci_low"].min()) * 0.9)
    hi = max(2.0, float(t["ci_high"].max()) * 1.1)
    return interval_chart(rows, ["odds ratio"], title=f"H1-H3: odds of a faithful trace ({outcome})",
                          x_label="odds ratio (log scale; > 1 = more often faithful than the comparison)",
                          x_min=lo, x_max=hi, log=True, ref=1.0, fmt=lambda v: f"{v:g}")


def main() -> None:
    cfg = load_experiment()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--judge", default=next(iter(cfg["judges"])), help="judge whose labels to use")
    ap.add_argument("--labels-root", type=Path, default=LABELS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--measure", choices=["main", "loose"], default="main")
    ap.add_argument("--threshold", type=float, default=0.6, help="reasoning-language threshold")
    ap.add_argument("--n-boot", type=int, default=2000, help="bootstrap resamples of questions")
    ap.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = ap.parse_args()

    seed, hints = cfg["seed"], list(cfg["hint_types"])
    outcome = "level 2" if args.measure == "main" else "level 1 or 2"
    runs = load_runs(args.root, args.models) if args.root.is_dir() else pd.DataFrame()
    labels = load_labels(args.judge, args.labels_root, runs)
    if not labels.empty and args.models:
        labels = labels[labels["model"].isin(args.models)]
    figures: dict[str, str | None] = {}

    if not runs.empty:
        hinted = with_influence(runs)
        det = hinted[~hinted["undetermined"]]
        det = det.assign(influenced=det["influenced"].astype(int))
        same = det[det["hint_lang"] == det["lang"]]
        figures["influence.svg"] = hint_rate_chart(
            same, "influenced", hints, "Influence: hinted runs that switch to the hinted option",
            "share of determined hinted runs (dot) with 95% bootstrap interval over questions",
            args.n_boot, seed) if not same.empty else None
        figures["h4_influence.svg"] = h4_chart(
            det, "influenced", "H4: influence of the expert hint, English vs. the question's language",
            "share of determined hinted runs, 95% bootstrap interval over questions", args.n_boot, seed)
        figures["reasoning_language.svg"] = language_chart(runs, args.threshold, args.n_boot, seed)

    data = usable_labels(labels, args.measure)
    if not data.empty:
        same = data[data["hint_lang"] == data["lang"]]
        figures["faithfulness.svg"] = hint_rate_chart(
            same, "faithful", hints, f"Faithfulness: influenced traces that admit the hint ({outcome})",
            f"share of influenced traces, judge {args.judge}, 95% bootstrap interval over questions",
            args.n_boot, seed) if not same.empty else None
        figures["h4_faithfulness.svg"] = h4_chart(
            data, "faithful", f"H4: faithfulness with the expert hint, English vs. the question's language ({outcome})",
            f"share of influenced traces, judge {args.judge}, 95% bootstrap interval over questions",
            args.n_boot, seed)
        figures["regression.svg"] = regression_chart(same, outcome)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    expected = ["influence.svg", "h4_influence.svg", "reasoning_language.svg",
                "faithfulness.svg", "h4_faithfulness.svg", "regression.svg"]
    for name in expected:
        svg = figures.get(name)
        if svg:
            (args.out_dir / name).write_text(svg, encoding="utf-8", newline="\n")
            print(f"Wrote {args.out_dir / name}")
    skipped = [n for n in expected if not figures.get(n)]
    if skipped:
        print("Skipped (no data yet): " + ", ".join(skipped))


if __name__ == "__main__":
    main()
