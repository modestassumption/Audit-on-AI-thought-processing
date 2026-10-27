"""Agreement between human labellers and the LLM judges on an exported labelling set.

    uv run python scripts/agreement.py --name practice

Reads every labels/human/<name>/<labeller>.csv (items.csv and key.csv are skipped) and every
judge's labels for the same runs, then prints Cohen's kappa for each pair on the main measure
(level 2 vs. not), the loose measure (level >= 1) and the raw three levels. Items marked
`exclude` or left blank by either side are dropped from that pair.
"""

from __future__ import annotations

import argparse
import itertools
import json

import pandas as pd

from cotaudit.analysis.agreement import cohen_kappa
from cotaudit.config import LABELS

MEASURES = {
    "3-level": lambda x: x,
    "main (2 vs 0/1)": lambda x: x == 2,
    "loose (1/2 vs 0)": lambda x: x >= 1,
}


def human_labels(folder) -> dict[str, pd.Series]:
    out = {}
    for path in sorted(folder.glob("*.csv")):
        if path.stem in ("items", "key"):
            continue
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").set_index("item_id")
        out[path.stem] = pd.to_numeric(df["level"], errors="coerce")
    return out


def judge_labels(key: pd.DataFrame) -> dict[str, pd.Series]:
    by_run = key.set_index("run_id")["item_id"]
    out = {}
    for judge_dir in sorted(p for p in LABELS.iterdir() if p.is_dir() and p.name != "human"):
        levels = {}
        for path in judge_dir.glob("20*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                if rec["trace_run_id"] in by_run.index and rec["level"] is not None:
                    levels[by_run[rec["trace_run_id"]]] = rec["level"]
        if levels:
            out[f"judge:{judge_dir.name}"] = pd.Series(levels, dtype=float)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    folder = LABELS / "human" / args.name
    key = pd.read_csv(folder / "key.csv", dtype=str, encoding="utf-8-sig")
    raters = human_labels(folder) | judge_labels(key)
    if len(raters) < 2:
        raise SystemExit(f"Need at least two raters, found {list(raters)}")

    rows = []
    for (na, a), (nb, b) in itertools.combinations(raters.items(), 2):
        both = pd.concat([a, b], axis=1, join="inner").dropna()
        row = {"pair": f"{na} vs {nb}", "n": len(both)}
        for name, f in MEASURES.items():
            row[name] = round(cohen_kappa(list(f(both.iloc[:, 0])), list(f(both.iloc[:, 1]))), 3) if len(both) else None
        rows.append(row)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
