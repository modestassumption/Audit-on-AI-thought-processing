"""Export a blinded sample of influenced traces for human labelling (proposal 4.6).

    uv run python scripts/export_labelling.py --name practice --langs en --n 40       # practice set
    uv run python scripts/export_labelling.py --name main --per-cell 30               # 360 = 3 models x 4 langs x 30

Writes labels/human/<name>/items.csv (what labellers see: no model name, no judge label) and
key.csv (item_id -> run, kept away from labellers). Each labeller copies items.csv to
<name>/<labeller>.csv and fills `level` (0/1/2 or exclude), `answer_mentions_hint` and `notes`
following docs/scoring_guide.md. For ml/zh, the second labeller fills `translation_en` with a
machine translation of the reasoning first and labels from that.
"""

from __future__ import annotations

import argparse
import hashlib

import pandas as pd

from cotaudit.analysis.influence import labelable, load_runs, with_influence
from cotaudit.config import LABELS, RUNS, load_experiment, load_hints
from cotaudit.prompts import render_hint

KEY_FIELDS = ["item_id", "run_id", "model", "qid", "lang", "condition", "hinted", "gold"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True, help="folder under labels/human/")
    ap.add_argument("--langs", nargs="+")
    ap.add_argument("--models", nargs="+")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--n", type=int, help="total items, sampled across everything selected")
    group.add_argument("--per-cell", type=int, help="items per model x language")
    args = ap.parse_args()

    seed, hints = load_experiment()["seed"], load_hints()
    rows = labelable(with_influence(load_runs(RUNS, args.models)))
    if args.langs:
        rows = rows[rows["lang"].isin(args.langs)]
    if rows.empty:
        raise SystemExit("No labelable influenced runs found")

    if args.per_cell:
        parts = []
        for (model, lang), g in rows.groupby(["model", "lang"]):
            if len(g) < args.per_cell:
                print(f"WARNING: only {len(g)} influenced traces for {model}/{lang}")
            parts.append(g.sample(min(len(g), args.per_cell), random_state=seed))
        sample = pd.concat(parts)
    else:
        sample = rows.sample(min(len(rows), args.n), random_state=seed)

    sample = sample.copy()
    sample["item_id"] = sample["run_id"].map(lambda r: hashlib.sha256(f"{args.name}:{r}".encode()).hexdigest()[:8])
    sample = sample.sort_values("item_id")  # shuffles models and languages together
    sample["hint_text"] = sample.apply(
        lambda r: render_hint(hints, r["hint_type"], r["hint_lang"], r["subject"], r["hinted"]), axis=1)
    items = sample[["item_id", "hint_type", "hint_text", "reasoning"]].assign(
        translation_en="", level="", answer_mentions_hint="", notes="")

    out = LABELS / "human" / args.name
    out.mkdir(parents=True, exist_ok=True)
    items.to_csv(out / "items.csv", index=False, encoding="utf-8-sig")
    sample[KEY_FIELDS].to_csv(out / "key.csv", index=False, encoding="utf-8-sig")
    print(f"{len(items)} items -> {out}")
    print(sample.groupby(["model", "lang"]).size().to_string())


if __name__ == "__main__":
    main()
