"""Render every prompt in the experiment grid into data/conditions.jsonl.

The same prompts are sent to every model; runners pick the model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter

from cotaudit.config import DATA, load_experiment, load_hints, unreviewed_entries
from cotaudit.conditions import build_conditions


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--require-reviewed", action="store_true",
                    help="fail if any translated prompt text is still an unreviewed draft")
    args = ap.parse_args()

    cfg, hints = load_experiment(), load_hints()
    pending = unreviewed_entries(hints, cfg["languages"])
    if pending:
        print(f"WARNING: {len(pending)} unreviewed translation entries:", file=sys.stderr)
        for p in pending:
            print(f"  - {p}", file=sys.stderr)
        if args.require_reviewed:
            sys.exit(1)

    questions = [json.loads(ln) for ln in (DATA / "questions.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = build_conditions(questions, cfg, hints)
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    (DATA / "conditions.jsonl").write_text(text, encoding="utf-8", newline="\n")

    counts = Counter("baseline" if r["hint_type"] == "none" else
                     "h4" if r["hint_lang"] != r["lang"] else "hinted" for r in rows)
    print(f"{len(rows)} conditions per model {dict(counts)}")
    print(f"sha256 {hashlib.sha256(text.encode('utf-8')).hexdigest()}")


if __name__ == "__main__":
    main()
