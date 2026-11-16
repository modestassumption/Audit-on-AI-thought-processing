"""Check answer extraction on logged runs (proposal week 3: "check answer extraction").

    uv run python scripts/check_extraction.py                         # every model in runs/
    uv run python scripts/check_extraction.py --models r1-distill-llama-8b --sample 10
    uv run python scripts/check_extraction.py --score results/extraction/hand_check.csv

For each model and language it re-reads the answer section with the current extractor and reports:
how often a letter was found, which rule found it ("Answer: X" is the format every prompt asks
for), runs with more than one candidate letter, runs cut off before an answer, and runs whose
logged `answer` differs from what the current extractor gives (logged with an older extractor).

Files written to --out-dir:
  failures.csv    every run with no letter or with conflicting letters, for a look by hand
  hand_check.csv  (--sample N) N extracted runs per model and language with an empty
                  `hand_answer` column; fill it in, then run --score on it
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pandas as pd

from cotaudit.analysis.influence import load_runs
from cotaudit.config import RUNS
from cotaudit.extract import candidate_letters, extract_with_rule

RULE_NAMES = ["label", "boxed", "phrase", "bare"]
CSV_FIELDS = ["run_id", "model", "lang", "condition", "rep", "logged", "extracted", "rule",
              "candidates", "finish_reason", "think_closed", "answer_tail"]


def pct(k: int, n: int) -> str:
    return "-" if n == 0 else f"{100 * k / n:.0f}%"


def md_table(rows: list[dict]) -> str:
    cols = list(rows[0])
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(lines)


def is_cut_off(r) -> bool:
    return r.get("finish_reason") == "length" or r.get("think_closed") is False


def recheck(df: pd.DataFrame) -> pd.DataFrame:
    """Add extracted / rule / candidates / cut_off columns from each run's answer section."""
    out = df.copy()
    texts = [c if isinstance(c, str) else None for c in out["content"]]
    found = [extract_with_rule(c) for c in texts]
    out["extracted"] = [f[0] for f in found]
    out["rule"] = [f[1] for f in found]
    out["candidates"] = ["".join(sorted(candidate_letters(c))) for c in texts]
    out["cut_off"] = [is_cut_off(r) for r in out.to_dict("records")]
    reasoning = [c if isinstance(c, str) else "" for c in out.get("reasoning", pd.Series("", index=out.index))]
    out["undecoded"] = [looks_undecoded((t or "") + r) for t, r in zip(texts, reasoning)]
    return out


def looks_undecoded(text: str) -> bool:
    """Byte-level BPE symbols instead of text ("ĊĊAnswer:ĠD"): the tokenizer wasn't applied on decode."""
    return text.count("Ġ") + text.count("Ċ") >= 3


def summary(df: pd.DataFrame) -> list[dict]:
    rows = []
    for (model, lang), g in df.groupby(["model", "lang"]):
        n = len(g)
        logged = g["answer"] if "answer" in g else pd.Series([None] * n, index=g.index)
        stale = (logged.fillna("") != g["extracted"].fillna("")).sum()
        row = {
            "model": model, "lang": lang, "runs": n,
            "extracted": pct(g["extracted"].notna().sum(), n),
            "cut off": pct(g["cut_off"].sum(), n),
            "empty answer section": pct(g["content"].fillna("").str.strip().eq("").sum(), n),
            "undecoded tokens": int(g["undecoded"].sum()),
        }
        for rule in RULE_NAMES:
            row[f"via {rule}"] = pct((g["rule"] == rule).sum(), n)
        row["conflicting letters"] = int((g["candidates"].str.len() > 1).sum())
        row["logged differs"] = int(stale)
        rows.append(row)
    return rows


def csv_row(r: dict) -> dict:
    tail = (r.get("content") or "").strip()[-300:].replace("\r", " ")
    return {
        "run_id": r["run_id"], "model": r["model"], "lang": r["lang"], "condition": r["condition"],
        "rep": r.get("rep"), "logged": r.get("answer"), "extracted": r["extracted"], "rule": r["rule"],
        "candidates": r["candidates"], "finish_reason": r.get("finish_reason"),
        "think_closed": r.get("think_closed"), "answer_tail": tail,
    }


def write_csv(path: Path, rows: list[dict], extra: list[str] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:   # BOM so Excel shows hi/zh/ml text
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS + list(extra))
        w.writeheader()
        w.writerows(rows)


def sample_rows(df: pd.DataFrame, per_cell: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for _, g in df[df["extracted"].notna()].groupby(["model", "lang"]):
        recs = g.to_dict("records")
        rows += [{**csv_row(r), "hand_answer": ""} for r in rng.sample(recs, min(per_cell, len(recs)))]
    return rows


def score(path: Path) -> str:
    """Agreement between the extractor and hand answers in a filled-in hand_check.csv."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("hand_answer", "").strip()]
    if not rows:
        raise SystemExit(f"No filled-in hand_answer values in {path}")
    cells: dict[tuple[str, str], list[bool]] = {}
    for r in rows:
        hand = r["hand_answer"].strip().upper()
        hand = "" if hand in {"NONE", "-", "?"} else hand
        cells.setdefault((r["model"], r["lang"]), []).append(hand == (r["extracted"] or ""))
    table = [{"model": m, "lang": lang, "checked": len(v), "agree": sum(v), "agreement": pct(sum(v), len(v))}
             for (m, lang), v in sorted(cells.items())]
    total = [ok for v in cells.values() for ok in v]
    misses = [r for r in rows if r["hand_answer"].strip().upper() != (r["extracted"] or "")]
    lines = ["# Extraction hand check", md_table(table),
             f"Overall: {sum(total)}/{len(total)} ({pct(sum(total), len(total))})"]
    if misses:
        lines.append("Disagreements:\n\n" + "\n".join(
            f"- {r['run_id']} ({r['model']}, {r['lang']}): extractor {r['extracted'] or 'none'}, "
            f"hand {r['hand_answer'].strip()}" for r in misses))
    return "\n\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=RUNS, help="runs folder (runs/smoke works too)")
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--out-dir", type=Path, default=Path("results/extraction"))
    ap.add_argument("--sample", type=int, default=0, help="write N extracted runs per model and language to hand_check.csv")
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--score", type=Path, help="score a filled-in hand_check.csv and exit")
    args = ap.parse_args()

    if args.score:
        print(score(args.score))
        return

    df = load_runs(args.root, args.models)
    if df.empty:
        raise SystemExit(f"No runs found under {args.root}")
    df = recheck(df)

    print("# Answer extraction check\n\n" + md_table(summary(df)) + "\n")
    if (n_raw := int(df["undecoded"].sum())):
        print(f"WARNING: {n_raw} runs contain byte-level tokens (Ġ/Ċ) instead of text: the tokenizer was "
              "broken when they ran, so their prompts may have been garbled too. Rerun them.\n")
    bad = df[df["extracted"].isna() | (df["candidates"].str.len() > 1)]
    write_csv(args.out_dir / "failures.csv", [csv_row(r) for r in bad.to_dict("records")])
    print(f"{len(bad)} runs with no letter or conflicting letters -> {args.out_dir / 'failures.csv'}")
    if args.sample:
        rows = sample_rows(df, args.sample, args.seed)
        write_csv(args.out_dir / "hand_check.csv", rows, extra=["hand_answer"])
        print(f"{len(rows)} runs to check by hand -> {args.out_dir / 'hand_check.csv'}")


if __name__ == "__main__":
    main()
