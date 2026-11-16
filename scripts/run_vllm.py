"""Run conditions on a local vLLM model (DeepSeek-R1-Distill-Llama-8B), for Kaggle GPUs.

Kaggle (GPU T4 x2) notebook cell (or use notebooks/kaggle_r1_distill.ipynb):
    !git clone https://github.com/modestassumption/Audit-on-AI-thought-processing.git
    %cd Audit-on-AI-thought-processing
    !pip install -q -e ".[kaggle]"
    !python scripts/run_vllm.py --model r1-distill-llama-8b --tp 2 --dtype half --n-questions 5

Results are appended to runs/<model>/ in batches, so a session that times out loses at most one
batch. Download the runs/ folder (or commit it) before the session ends.

--max-hours stops cleanly before starting a batch once that much time has passed, so a run
finishes inside Kaggle's 12-hour session limit and the weekly GPU quota. The GPU time used is
printed at the end for docs/compute.md.
"""

from __future__ import annotations

import argparse
import time

from cotaudit.config import load_experiment
from cotaudit.runlog import RunLog
from cotaudit.runners.base import (
    add_filter_args, load_conditions, make_record, max_completion_tokens, select_conditions,
)
from cotaudit.runners.vllm_runner import VLLMRunner


def hours(seconds: float) -> str:
    return f"{seconds / 3600:.2f} h"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_filter_args(ap)
    ap.add_argument("--tp", type=int, default=1, help="tensor parallel size (2 on Kaggle T4 x2)")
    ap.add_argument("--dtype", default="auto", help="'half' on T4 GPUs (no bf16 support)")
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--max-hours", type=float, help="don't start a new batch after this many hours")
    ap.add_argument("--gpu-memory-utilization", type=float, help="vLLM default 0.9; lower it if loading runs out of memory")
    ap.add_argument("--enforce-eager", action="store_true", help="skip CUDA graph capture (less memory, slower)")
    args = ap.parse_args()

    started = time.time()
    cfg = load_experiment()
    model_cfg = cfg["models"][args.model]
    if model_cfg["provider"] != "vllm":
        raise SystemExit(f"{args.model} is a {model_cfg['provider']} model; use run_groq.py")

    log = RunLog(args.model, tag=args.tag)
    todo = select_conditions(load_conditions(), args, log.completed_prompts())
    print(f"{args.model}: {len(todo)} runs to do -> {log.dir}")
    if not todo:
        return

    engine_args = {}
    if args.gpu_memory_utilization:
        engine_args["gpu_memory_utilization"] = args.gpu_memory_utilization
    if args.enforce_eager:
        engine_args["enforce_eager"] = True
    runner = VLLMRunner(model_cfg, max_completion_tokens(cfg), args.tp, args.dtype, cfg["seed"], **engine_args)
    print(f"model loaded after {hours(time.time() - started)}")

    done = 0
    for start in range(0, len(todo), args.batch_size):
        if args.max_hours and time.time() - started > args.max_hours * 3600:
            print(f"--max-hours {args.max_hours} reached; run the same command again to continue")
            break
        batch = todo[start : start + args.batch_size]
        outs = runner.generate_batch([c["prompt"] for c in batch])
        for cond, out in zip(batch, outs):
            log.write(make_record(args.model, model_cfg, runner.params, cond, out))
        done += len(batch)
        print(f"{done}/{len(todo)} logged ({hours(time.time() - started)})")

    print(f"Logged {done} runs, {len(todo) - done} left. GPU time this session: {hours(time.time() - started)}")


if __name__ == "__main__":
    main()
