"""Run conditions on a local vLLM model (DeepSeek-R1-Distill-Llama-8B), for Kaggle GPUs.

Kaggle (GPU T4 x2) notebook cell:
    !git clone https://github.com/modestassumption/Audit-on-AI-thought-processing.git
    %cd Audit-on-AI-thought-processing
    !pip install -q -e ".[kaggle]"
    !python scripts/run_vllm.py --model r1-distill-llama-8b --tp 2 --dtype half --n-questions 5

Results are appended to runs/<model>/ in batches, so a session that times out loses at most one
batch. Download the runs/ folder (or commit it) before the session ends.
"""

from __future__ import annotations

import argparse

from cotaudit.config import load_experiment
from cotaudit.runlog import RunLog
from cotaudit.runners.base import (
    add_filter_args, load_conditions, make_record, max_completion_tokens, select_conditions,
)
from cotaudit.runners.vllm_runner import VLLMRunner


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_filter_args(ap)
    ap.add_argument("--tp", type=int, default=1, help="tensor parallel size (2 on Kaggle T4 x2)")
    ap.add_argument("--dtype", default="auto", help="'half' on T4 GPUs (no bf16 support)")
    ap.add_argument("--batch-size", type=int, default=256)
    args = ap.parse_args()

    cfg = load_experiment()
    model_cfg = cfg["models"][args.model]
    if model_cfg["provider"] != "vllm":
        raise SystemExit(f"{args.model} is a {model_cfg['provider']} model; use run_groq.py")

    log = RunLog(args.model)
    todo = select_conditions(load_conditions(), args, log.completed_ids())
    print(f"{args.model}: {len(todo)} runs to do -> {log.dir}")
    if not todo:
        return
    runner = VLLMRunner(model_cfg, max_completion_tokens(cfg), args.tp, args.dtype, cfg["seed"])

    for start in range(0, len(todo), args.batch_size):
        batch = todo[start : start + args.batch_size]
        outs = runner.generate_batch([c["prompt"] for c in batch])
        for cond, out in zip(batch, outs):
            log.write(make_record(args.model, model_cfg, runner.params, cond, out))
        print(f"{start + len(batch)}/{len(todo)} logged")


if __name__ == "__main__":
    main()
