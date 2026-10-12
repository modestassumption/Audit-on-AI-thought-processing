"""Run conditions on a Groq-hosted model (gpt-oss-20b, qwen3-32b), resuming where it left off.

    uv run python scripts/run_groq.py --model qwen3-32b --n-questions 5 --langs en hi
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

from cotaudit.config import RUNS, load_experiment
from cotaudit.runlog import RunLog, now_utc
from cotaudit.runners.base import (
    add_filter_args, load_conditions, make_record, max_completion_tokens, select_conditions,
)
from cotaudit.runners.groq_runner import GroqRunner, QuotaExhausted, keys_from_env


def run(args: argparse.Namespace, root: Path = RUNS) -> list[dict]:
    """Run every selected, not-yet-logged condition; return the records written this call."""
    load_dotenv()
    cfg = load_experiment()
    model_cfg = cfg["models"][args.model]
    if model_cfg["provider"] != "groq":
        raise SystemExit(f"{args.model} is a {model_cfg['provider']} model; use run_vllm.py")

    log = RunLog(args.model, root)
    todo = select_conditions(load_conditions(), args, log.completed_ids())
    print(f"{args.model}: {len(todo)} runs to do -> {log.dir}")
    runner = GroqRunner(model_cfg, max_completion_tokens(cfg), keys_from_env())

    written = []
    for i, cond in enumerate(todo, 1):
        try:
            out = runner.generate(cond["prompt"])
        except QuotaExhausted as err:
            print(f"Stopping: {err}. Rerun later to resume.")
            break
        except Exception as err:  # logged and retried on the next invocation
            log.write_error({"timestamp_utc": now_utc(), "condition_id": cond["condition_id"],
                             "error": f"{type(err).__name__}: {err}"})
            print(f"[{i}/{len(todo)}] ERROR {cond['condition_id']}: {err}")
            continue
        rec = make_record(args.model, model_cfg, runner.params, cond, out)
        log.write(rec)
        written.append(rec)
        print(f"[{i}/{len(todo)}] {cond['condition_id']} -> {rec['answer']} "
              f"(gold {rec['gold']}, hinted {rec['hinted']}, {rec['finish_reason']}, {out['latency_s']}s)")

    print(f"Done: {len(written)} logged, answers {dict(Counter(r['answer'] for r in written))}")
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_filter_args(ap)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
