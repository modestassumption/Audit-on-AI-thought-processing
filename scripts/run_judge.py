"""Label influenced reasoning traces with the keyword filter and an LLM judge, resuming where it left off.

    uv run python scripts/run_judge.py --judge gpt-oss-120b --limit 20      # first check
    uv run python scripts/run_judge.py --judge qwen3.8-27b --models gpt-oss-20b
    uv run python scripts/run_judge.py --judge gpt-oss-120b --review-sample   # flag counts + review list

Targets every influenced run in runs/ (see cotaudit.analysis.influence) whose reasoning is
present and not truncated. Labels go to labels/<judge>/<date>-<tag>.jsonl; cases whose quote is
not found in the trace are marked `needs_manual`. Each label stores keyword hits on the reasoning
(`kw_hits`) and on the final answer (`content_kw_hits`) and its review `flags` (F1/F2/Q, D1).
--review-sample makes no API calls: it counts the flags and writes labels/<judge>/review_sample.csv.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

import pandas as pd
from dotenv import load_dotenv

from cotaudit.analysis.influence import labelable, load_runs, with_influence
from cotaudit.config import LABELS, RUNS, load_experiment, load_hints
from cotaudit.data.select import in_shard
from cotaudit.judge.keywords import (REVIEW_CAP, find_hits, load_keywords, load_questions, question_text,
                                     review_flags, review_sample)
from cotaudit.judge.llm_judge import build_prompt, load_template, needs_manual, parse_response
from cotaudit.runlog import RunLog, now_utc, run_id
from cotaudit.runners.base import parse_shard
from cotaudit.runners.groq_runner import GroqRunner, QuotaExhausted, keys_from_env

TRACE_FIELDS = ("model", "qid", "subject", "stratum", "lang", "hint_type", "hint_lang", "condition", "hinted", "gold")


def targets(args: argparse.Namespace) -> list[dict]:
    rows = labelable(with_influence(load_runs(RUNS, args.models)), influenced_only=not args.all_hinted)
    if args.shard:
        rows = rows[rows["qid"].map(lambda q: in_shard(q, *args.shard))]
    return rows.to_dict("records")


def load_labels(judge: str) -> list[dict]:
    return [json.loads(ln) for path in sorted((LABELS / judge).glob("20*.jsonl"))
            for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def report_review_sample(judge: str, seed: int) -> None:
    """Print flag counts by language and write the human-review list (D1)."""
    labels = load_labels(judge)
    counts = Counter((f, r["lang"]) for r in labels for f in r.get("flags", []))
    table = pd.Series(counts, dtype=int).unstack(fill_value=0) if counts else pd.DataFrame()
    print(f"{judge}: {len(labels)} labels; flag counts by language:\n{table.to_string() if counts else 'none'}")
    n1, n2 = sum(v for (f, _), v in counts.items() if f == "F1"), sum(v for (f, _), v in counts.items() if f == "F2")
    sample = review_sample(labels, seed)
    mode = "sampled F1 (equal per language) + all F2" if n1 + n2 > REVIEW_CAP else "all F1 and F2"
    print(f"F1 + F2 = {n1 + n2} (cap {REVIEW_CAP}): reviewing {mode}, {len(sample)} traces")
    if sample:
        cols = ["run_id", "trace_run_id", "model", "lang", "condition", "level", "flags", "review_flag", "weight"]
        out = LABELS / judge / "review_sample.csv"
        pd.DataFrame(sample)[cols].assign(flags=lambda d: d["flags"].map(" ".join)).to_csv(
            out, index=False, encoding="utf-8-sig")
        print(f"-> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--judge", required=True, help="judge key from configs/experiment.yaml")
    ap.add_argument("--models", nargs="+", help="only traces from these models")
    ap.add_argument("--all-hinted", action="store_true", help="label every hinted run, not only influenced ones")
    ap.add_argument("--limit", type=int, help="stop after this many new labels")
    ap.add_argument("--shard", type=parse_shard, help="i/n share of questions, as for run_groq.py")
    ap.add_argument("--tag", help="log file suffix (default: this computer's name)")
    ap.add_argument("--review-sample", action="store_true",
                    help="no judging: count F1/F2/Q flags and write the human-review list")
    args = ap.parse_args()

    if args.review_sample:
        report_review_sample(args.judge, load_experiment()["seed"])
        return

    load_dotenv()
    cfg, hints, keywords, template = load_experiment(), load_hints(), load_keywords(), load_template()
    questions = load_questions()
    judge_cfg = cfg["judges"][args.judge]
    log = RunLog(args.judge, LABELS, args.tag)
    done = log.completed_ids()
    todo = [t for t in targets(args) if run_id(args.judge, t["run_id"]) not in done]
    todo = todo[: args.limit] if args.limit else todo
    print(f"{args.judge}: {len(todo)} traces to label -> {log.dir}")
    runner = GroqRunner(judge_cfg, judge_cfg["max_completion_tokens"], keys_from_env())

    levels, flag_counts = Counter(), Counter()
    for i, trace in enumerate(todo, 1):
        try:
            out = runner.generate(build_prompt(template, hints, trace, questions))
        except QuotaExhausted as err:
            print(f"Stopping: {err}. Rerun later to resume.")
            break
        except Exception as err:
            log.write_error({"timestamp_utc": now_utc(), "trace_run_id": trace["run_id"],
                             "error": f"{type(err).__name__}: {err}"})
            print(f"[{i}/{len(todo)}] ERROR {trace['condition_id']}: {err}")
            continue
        verdict = parse_response(out["content"])
        manual = needs_manual(verdict, trace["reasoning"])
        q_text = question_text(questions.get(trace["qid"]), trace["lang"])
        kw = [find_hits(trace.get(field), keywords, trace["hint_type"], trace["lang"], trace["hint_lang"], q_text)
              for field in ("reasoning", "content")]
        flags = review_flags(verdict["level"] if verdict else None, kw[0], manual)
        log.write({
            "run_id": run_id(args.judge, trace["run_id"]),
            "trace_run_id": trace["run_id"],
            "judge": args.judge,
            "judge_model_id": judge_cfg["model_id"],
            "timestamp_utc": now_utc(),
            "params": runner.params,
            **{k: trace[k] for k in TRACE_FIELDS},
            "influenced": bool(trace["influenced"]),
            "level": verdict["level"] if verdict else None,
            "quote": verdict["quote"] if verdict else None,
            "restate_only": verdict["restate_only"] if verdict else None,
            "rationale": verdict["rationale"] if verdict else None,
            "needs_manual": manual,
            "kw_hits": kw[0],
            "content_kw_hits": kw[1],
            "flags": flags,
            "judge_content": out["content"],
            "judge_reasoning": out["reasoning"],
            "model_returned": out["model_returned"],
            "usage": out["usage"],
        })
        levels[verdict["level"] if verdict else "?"] += 1
        flag_counts.update(flags)
        print(f"[{i}/{len(todo)}] {trace['model']} {trace['condition_id']} -> level "
              f"{verdict['level'] if verdict else '?'}{' (manual: ' + manual + ')' if manual else ''}")

    print(f"Done: levels {dict(levels)}, flags {dict(flag_counts)}")


if __name__ == "__main__":
    main()
