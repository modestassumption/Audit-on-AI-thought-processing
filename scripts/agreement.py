"""Agreement between human labellers and the LLM judges on an exported labelling set.

    uv run python scripts/agreement.py --name practice

Reads every labels/human/<name>/<labeller>.csv (items.csv, key.csv and agreement.csv are skipped) and every
judge's labels for the same runs. `adjudicated.csv` is a rater named "adjudicated". For each pair
of raters and each measure (main = level 2 vs. not, the 0.70 target; loose = level >= 1; the raw
three levels) it gives n, percent agreement, each rater's class prevalence, unweighted Cohen's
kappa and a 95% bootstrap interval (2,000 resamples of traces, seeded; resamples with no defined
kappa are dropped and counted in `boot_dropped`). No weighted kappa (D6).

Slices: pooled, each language, each model, and two language groups that are never merged:
direct (en, hi: both labellers read the original) and translation-mediated (zh, ml). A judge
that is also a tested model (qwen3.8-27b) is split into its own and other models' traces.
Items whose run is no longer current, or was re-run after export (so its reasoning is not what
the labellers saw), are left out for every rater and counted on stderr (current_items). Items
marked `exclude`, left blank or not labelled by either side are dropped from that pair and counted
in `excluded`. Only the `level` column is compared; `restate_only` (used for the D3
sensitivity check) and the other columns are ignored. The table is printed and written to
labels/human/<name>/agreement.csv.
"""

from __future__ import annotations

import argparse
import itertools
import json

import pandas as pd

from cotaudit.analysis.agreement import agreement_stats
from cotaudit.analysis.influence import current_items, current_labels, load_runs
from cotaudit.config import LABELS, RUNS, load_experiment

MEASURES = {
    "main (2 vs 0/1)": lambda x: x == 2,
    "loose (1/2 vs 0)": lambda x: x >= 1,
    "3-level": lambda x: x,
}
GROUPS = {"direct (en+hi)": ("en", "hi"), "translation-mediated (zh+ml)": ("zh", "ml")}


def human_labels(folder) -> dict[str, pd.Series]:
    out = {}
    for path in sorted(folder.glob("*.csv")):
        if path.stem in ("items", "key", "agreement"):  # agreement.csv is this script's output
            continue
        df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").drop_duplicates("item_id").set_index("item_id")
        out[path.stem] = pd.to_numeric(df["level"], errors="coerce")
    return out


def judge_labels(key: pd.DataFrame, runs: pd.DataFrame | None) -> dict[str, pd.Series]:
    """Each judge's level per item. Only labels still current for the logged runs count (none on a
    trace re-run since it was judged); if a trace has several, the first one is used."""
    by_run = key.set_index("run_id")["item_id"]
    out = {}
    for judge_dir in sorted(p for p in LABELS.iterdir() if p.is_dir() and p.name != "human"):
        records = [json.loads(line) for path in sorted(judge_dir.glob("20*.jsonl"))
                   for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if runs is not None:
            records = current_labels(records, runs)
        levels = {}
        for rec in records:
            item = by_run.get(rec.get("trace_run_id"))
            if item is not None and rec.get("level") is not None:
                levels.setdefault(item, rec["level"])
        if levels:
            out[f"judge:{judge_dir.name}"] = pd.Series(levels, dtype=float)
    return out


def slices(key: pd.DataFrame, raters: tuple[str, str]) -> list[tuple[str, pd.Index]]:
    """(slice name, item_ids) for one pair of raters; empty slices are left out.

    `key` is key.csv indexed by item_id. The own/other split is added for a judge whose name is
    also a model in the key.
    """
    out = [("pooled", key.index)]
    out += [(f"group: {name}", key.index[key["lang"].isin(langs)]) for name, langs in GROUPS.items()]
    out += [(f"lang: {lang}", key.index[key["lang"] == lang]) for lang in sorted(key["lang"].unique())]
    out += [(f"model: {m}", key.index[key["model"] == m]) for m in sorted(key["model"].unique())]
    for judge in sorted({r.removeprefix("judge:") for r in raters if r.startswith("judge:")}):
        if judge in set(key["model"]):
            out += [(f"{judge} own traces", key.index[key["model"] == judge]),
                    (f"{judge} other models' traces", key.index[key["model"] != judge])]
    return [(name, items) for name, items in out if len(items)]


def agreement_table(key: pd.DataFrame, raters: dict[str, pd.Series], seed: int, n_boot: int = 2000) -> pd.DataFrame:
    """One row per pair x slice x measure."""
    rows = []
    for (na, a), (nb, b) in itertools.combinations(raters.items(), 2):
        for name, items in slices(key, (na, nb)):
            both = pd.concat([a.reindex(items), b.reindex(items)], axis=1).dropna()
            for measure, f in MEASURES.items():
                row = {"pair": f"{na} vs {nb}", "slice": name, "measure": measure, "n": len(both),
                       "excluded": len(items) - len(both)}
                if len(both):
                    row |= agreement_stats(list(f(both.iloc[:, 0])), list(f(both.iloc[:, 1])), seed, n_boot)
                rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    folder = LABELS / "human" / args.name
    key = pd.read_csv(folder / "key.csv", dtype=str, encoding="utf-8-sig").drop_duplicates("item_id")
    runs = load_runs(RUNS) if RUNS.is_dir() else None
    try:
        current = current_items(folder, runs)
    except ValueError as err:
        raise SystemExit(str(err)) from None
    key = key[key["item_id"].map(current).fillna(False).astype(bool)]
    raters = {name: levels.reindex(key["item_id"]) for name, levels in human_labels(folder).items()}
    raters |= judge_labels(key, runs)
    if len(raters) < 2:
        raise SystemExit(f"Need at least two raters, found {list(raters)}")

    table = agreement_table(key.set_index("item_id"), raters, load_experiment()["seed"])
    table.to_csv(folder / "agreement.csv", index=False, encoding="utf-8-sig")
    print(table.to_string(index=False))
    print(f"-> {folder / 'agreement.csv'}")


if __name__ == "__main__":
    main()
