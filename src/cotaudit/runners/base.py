"""Shared pieces of the run scripts: condition filtering and the logged record shape."""

from __future__ import annotations

import argparse
import json

from cotaudit.config import DATA
from cotaudit.extract import extract_answer
from cotaudit.runlog import now_utc, run_id

CONDITION_FIELDS = (
    "condition_id", "qid", "subject", "stratum", "lang", "hint_type", "hint_lang",
    "rep", "gold", "hinted", "prompt_sha256",
)


def add_filter_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--model", required=True, help="model key from configs/experiment.yaml")
    ap.add_argument("--n-questions", type=int, help="only the first N questions (sorted by qid)")
    ap.add_argument("--langs", nargs="+", help="subset of languages")
    ap.add_argument("--hint-types", nargs="+", help="subset of: none expert metadata leaked")
    ap.add_argument("--no-h4", action="store_true", help="skip cross-lingual (H4) conditions")
    ap.add_argument("--limit", type=int, help="stop after this many new runs")


def load_conditions() -> list[dict]:
    lines = (DATA / "conditions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def select_conditions(rows: list[dict], args: argparse.Namespace, done: set[str]) -> list[dict]:
    if args.n_questions:
        keep = set(sorted({r["qid"] for r in rows})[: args.n_questions])
        rows = [r for r in rows if r["qid"] in keep]
    if args.langs:
        rows = [r for r in rows if r["lang"] in args.langs]
    if args.hint_types:
        rows = [r for r in rows if r["hint_type"] in args.hint_types]
    if args.no_h4:
        rows = [r for r in rows if r["hint_type"] == "none" or r["hint_lang"] == r["lang"]]
    rows = [r for r in rows if run_id(args.model, r["condition_id"]) not in done]
    return rows[: args.limit] if args.limit else rows


def max_completion_tokens(cfg: dict) -> int:
    return cfg["reasoning_cap_tokens"] + cfg["answer_budget_tokens"]


def make_record(model: str, model_cfg: dict, params: dict, cond: dict, out: dict) -> dict:
    """`out` holds the provider result: reasoning, content, model_returned, finish_reason, usage, ..."""
    return {
        "run_id": run_id(model, cond["condition_id"]),
        "model": model,
        "model_id": model_cfg["model_id"],
        "provider": model_cfg["provider"],
        "timestamp_utc": now_utc(),
        "params": params,
        **{k: cond[k] for k in CONDITION_FIELDS},
        **out,
        "answer": extract_answer(out.get("content")),
    }
