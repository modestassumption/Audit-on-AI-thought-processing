"""Summarise logged runs: answer extraction, truncation, accuracy, influence rates, token use.

    uv run python scripts/report_runs.py                       # every model in runs/
    uv run python scripts/report_runs.py --tpd gpt-oss-20b=200000 --keys 7 --out results/pilot.md

--tpd gives each model's tokens-per-day limit per Groq key (Settings -> Limits in the console),
so the report can project how many key-days the full 6,900-run grid needs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import influence_counts, load_runs, noise_rate, wilson, with_influence
from cotaudit.config import RUNS

FULL_GRID = 6900


def pct(x: float) -> str:
    return "-" if pd.isna(x) else f"{100 * x:.0f}%"


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def is_truncated(g: pd.DataFrame) -> pd.Series:
    """Hit the token cap, or (vLLM) never closed the </think> block."""
    unclosed = g["think_closed"].eq(False) if "think_closed" in g else False
    return g["finish_reason"].eq("length") | unclosed


def run_health(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (model, lang), g in df.groupby(["model", "lang"]):
        base = g[g["hint_type"] == "none"]
        reps = base.pivot_table(index="qid", columns="rep", values="answer", aggfunc="first")
        both = reps.dropna() if {1, 2} <= set(reps.columns) else None
        out.append({
            "model": model, "lang": lang, "runs": len(g), "questions": g["qid"].nunique(),
            "reasoning returned": pct(g["reasoning"].fillna("").str.len().gt(0).mean()),
            "answer extracted": pct(g["answer"].notna().mean()),
            "truncated": pct(is_truncated(g).mean()),
            "baseline accuracy": pct((base["answer"] == base["gold"]).mean()),
            "baseline reps agree": pct((both[1] == both[2]).mean()) if both is not None and len(both) else "-",
            "picked hint, no hint": pct((base["answer"] == base["hinted"]).mean()),
        })
    return pd.DataFrame(out)


def influence_rates(hinted: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (model, lang, cond), g in hinted.groupby(["model", "lang", "condition"]):
        det = g[~g["undetermined"]]
        k, n = int(det["influenced"].sum()), len(det)
        lo, hi = wilson(k, n)
        out.append({
            "model": model, "lang": lang, "hint": cond, "runs": len(g), "determined": n,
            "picked hint, with hint": pct((g["answer"] == g["hinted"]).mean()),
            "influenced": k, "influence rate": pct(k / n if n else float("nan")),
            "95% CI": f"{pct(lo)}-{pct(hi)}",
            "influenced (rep1 only)": int(g["influenced_rep1"].sum()),
        })
    return pd.DataFrame(out)


def token_projection(df: pd.DataFrame, tpd: dict[str, int], keys: int) -> pd.DataFrame:
    out = []
    for model, g in df.groupby("model"):
        usage = pd.json_normalize(g["usage"].dropna().tolist())
        if usage.empty:
            continue
        total = usage["total_tokens"] if "total_tokens" in usage else usage["prompt_tokens"] + usage["completion_tokens"]
        projected = total.mean() * FULL_GRID
        row = {
            "model": model, "runs": len(g),
            "completion tokens mean": f"{usage['completion_tokens'].mean():.0f}",
            "completion tokens p95": f"{usage['completion_tokens'].quantile(0.95):.0f}",
            "total tokens / run": f"{total.mean():.0f}",
            "projected tokens, full grid": f"{projected / 1e6:.1f}M",
            "key-days needed": "-", f"days with {keys} keys": "-",
        }
        if model in tpd:
            key_days = projected / tpd[model]
            row["key-days needed"] = f"{key_days:.1f}"
            row[f"days with {keys} keys"] = f"{key_days / keys:.1f}"
        out.append(row)
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS)
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--tpd", nargs="*", default=[], help="model=tokens_per_day per key")
    ap.add_argument("--keys", type=int, default=7, help="Groq keys available")
    ap.add_argument("--out", type=Path, help="also write the report to this markdown file")
    args = ap.parse_args()

    df = load_runs(args.root, args.models)
    if df.empty:
        raise SystemExit(f"No runs found under {args.root}")
    tpd = {k: int(v) for k, v in (item.split("=") for item in args.tpd)}
    hinted = with_influence(df)

    sections = [
        "# Run report",
        "## Run health\n\n" + md_table(run_health(df)),
        "## Influence (hint picked, neither baseline picked it)\n\n" + md_table(influence_rates(hinted)),
        "## Influence status counts\n\nsplit = picked the hint, both baselines answered, exactly one "
        "baseline also picked it (not influenced).\n\n" + md_table(influence_counts(hinted)),
        "## Baseline noise rate\n\nAmong questions with both baselines answered and baseline 1 not on "
        "the hinted option, the share where baseline 2 picked it.\n\n"
        + md_table(noise_rate(df).assign(noise_rate=lambda t: t["noise_rate"].map(pct))),
        "## Token use and quota\n\n" + md_table(token_projection(df, tpd, args.keys)),
    ]
    report = "\n\n".join(sections) + "\n"
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8", newline="\n")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
