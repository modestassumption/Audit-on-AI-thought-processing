"""End-to-end check of the Groq pipeline on a few questions; logs under runs/smoke/.

    uv run python scripts/smoke_test.py --n 3

Runs both baselines + the three native-language hints in all four languages for each Groq
model, then reports whether reasoning came back, how often an answer was extracted, truncation,
and token use. Rerunning skips completed runs (resume check).
"""

from __future__ import annotations

import argparse
from statistics import mean

from cotaudit.config import RUNS, load_experiment
from run_groq import run


def summarise(model: str, records: list[dict]) -> None:
    if not records:
        print(f"{model}: nothing new logged")
        return
    n = len(records)
    usage = [r["usage"] or {} for r in records]
    print(f"\n== {model}: {n} runs ==")
    print(f"  reasoning returned : {sum(bool(r['reasoning']) for r in records)}/{n}")
    print(f"  answer extracted   : {sum(r['answer'] is not None for r in records)}/{n}")
    print(f"  truncated (length) : {sum(r['finish_reason'] == 'length' for r in records)}/{n}")
    print(f"  correct            : {sum(r['answer'] == r['gold'] for r in records)}/{n}")
    print(f"  picked hinted (hinted conds): "
          f"{sum(r['answer'] == r['hinted'] for r in records if r['hint_type'] != 'none')}"
          f"/{sum(r['hint_type'] != 'none' for r in records)}")
    print(f"  completion tokens  : mean {mean(u.get('completion_tokens', 0) for u in usage):.0f}, "
          f"max {max(u.get('completion_tokens', 0) for u in usage)}")
    print(f"  models returned    : {sorted({r['model_returned'] for r in records})}")
    for r in records:
        if r["answer"] is None:
            print(f"  ! no answer: {r['condition_id']} content={str(r['content'])[-120:]!r}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=3, help="questions per model")
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--langs", nargs="+")
    args = ap.parse_args()

    cfg = load_experiment()
    models = args.models or [m for m, c in cfg["models"].items() if c["provider"] == "groq"]
    for model in models:
        run_args = argparse.Namespace(
            model=model, n_questions=args.n, langs=args.langs, hint_types=None,
            no_h4=True, limit=None,
        )
        records = run(run_args, root=RUNS / "smoke")
        summarise(model, records)


if __name__ == "__main__":
    main()
