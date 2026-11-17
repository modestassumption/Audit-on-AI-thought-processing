"""Label influenced reasoning traces with the keyword filter and an LLM judge, resuming where it left off.

    uv run python scripts/run_judge.py --judge gpt-oss-120b --limit 20      # first check
    uv run python scripts/run_judge.py --judge qwen3.8-27b --models gpt-oss-20b
    uv run python scripts/run_judge.py --judge gpt-oss-120b --review-sample   # flag counts + review list
    uv run python scripts/run_judge.py --judge qwen3.8-27b --key labels/human/main/key.csv   # second judge, the 360

Targets every influenced run in runs/ (see cotaudit.analysis.influence) whose reasoning is
present and not truncated. Labels go to labels/<judge>/<date>-<tag>.jsonl; cases whose quote is
not found in the trace are marked `needs_manual`. Each label stores keyword hits on the reasoning
(`kw_hits`) and on the final answer (`content_kw_hits`) and its review `flags` (F1/F2/Q, D1).
Traces are judged in a seeded order stratified by model x language x condition, so a partial run
is representative (D5). A request Groq rejects as too large is not retried: it is labelled
`needs_manual: too_large`. Other failed requests go to errors-<tag>.jsonl and are retried next run.
--review-sample makes no API calls: it prints the keyword mention rate and Level 2 rates per
model x language, counts the flags and writes labels/<judge>/review_sample.csv.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from cotaudit.analysis.influence import current_labels, label_is_current, labelable, load_runs, with_influence
from cotaudit.config import LABELS, RUNS, load_experiment, load_hints
from cotaudit.data.select import in_shard
from cotaudit.judge.keywords import (REVIEW_CAP, find_hits, keyword_summary, load_keywords, load_questions,
                                     question_text, review_flags, review_sample)
from cotaudit.judge.llm_judge import build_prompt, load_template, needs_manual, parse_response
from cotaudit.runlog import RunLog, now_utc, run_id
from cotaudit.runners.base import parse_shard
from cotaudit.runners.groq_runner import GroqRunner, QuotaExhausted, keys_from_env

TRACE_FIELDS = ("model", "qid", "subject", "stratum", "lang", "hint_type", "hint_lang", "condition", "hinted", "gold")


def targets(args: argparse.Namespace) -> list[dict]:
    rows = labelable(with_influence(load_runs(RUNS, args.models)), influenced_only=not args.all_hinted)
    if args.shard:
        rows = rows[rows["qid"].map(lambda q: in_shard(q, *args.shard))]
    if args.key:
        keep = set(pd.read_csv(args.key, dtype=str, encoding="utf-8-sig")["run_id"])
        rows = rows[rows["run_id"].isin(keep)]
    return rows.to_dict("records")


def judge_order(rows: list[dict], seed: int) -> list[dict]:
    """Seeded judging order, stratified by model x lang x condition (D5).

    Each stratum is shuffled and its traces are spread evenly over the whole run (trace i of n
    lands near position i/n), so stopping early leaves about the same share of every stratum
    judged. The order depends only on the seed and the set of traces, so a resumed run continues
    the same sequence.
    """
    rng = random.Random(seed)
    strata = defaultdict(list)
    for r in sorted(rows, key=lambda r: r["run_id"]):
        strata[(r["model"], r["lang"], r["condition"])].append(r)
    placed = []
    for key in sorted(strata):
        group = strata[key]
        rng.shuffle(group)
        placed += [((i + rng.random()) / len(group), r["run_id"], r) for i, r in enumerate(group)]
    return [r for _, _, r in sorted(placed, key=lambda t: t[:2])]


def too_large(err: Exception) -> bool:
    """Groq refused the request for its size (HTTP 413, or a "too large" message)."""
    return getattr(err, "status_code", None) == 413 or "too large" in str(err).lower()


def read_labels(judge: str) -> list[dict]:
    """Every label record logged for this judge, in file order."""
    return [json.loads(ln) for path in sorted((LABELS / judge).glob("20*.jsonl"))
            for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_labels(judge: str, runs: pd.DataFrame | None = None) -> list[dict]:
    """One label per run_id (the first, if two machines judged the same trace), influenced traces
    only: labels made with --all-hinted would otherwise count against the review cap. Given `runs`,
    labels on traces that are no longer current runs (dropped question, re-run prompt) are left out
    first, so a re-judged trace keeps its new label."""
    rows = read_labels(judge)
    if runs is not None:
        rows = current_labels(rows, runs)
    first = {}
    for r in rows:
        if r.get("influenced", True):
            first.setdefault(r["run_id"], r)
    return list(first.values())


def report_review_sample(judge: str, seed: int) -> None:
    """Print flag counts by language, the keyword and Level 2 rates, and write the human-review list (D1)."""
    labels = load_labels(judge, load_runs(RUNS) if RUNS.is_dir() else None)
    if labels:
        print("Keyword mention rate, language-switch share and Level 2 (with restate_only sensitivity):\n"
              + pd.DataFrame(keyword_summary(labels)).to_string(index=False))
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
    ap.add_argument("--key", type=Path, help="only traces whose run_id is in this key.csv "
                    "(labels/human/<name>/key.csv), e.g. the second judge on the 360")
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
    traces = targets(args)
    by_id = {t["run_id"]: t for t in traces}
    # A trace counts as judged only if its label is current: a trace re-run with a changed prompt
    # keeps its run_id, and its old label must not stop it from being judged again.
    done = {lab["trace_run_id"] for lab in read_labels(args.judge)
            if label_is_current(lab, by_id.get(lab.get("trace_run_id")))}
    todo = [t for t in judge_order(traces, cfg["seed"]) if t["run_id"] not in done]
    todo = todo[: args.limit] if args.limit else todo
    print(f"{args.judge}: {len(todo)} traces to label -> {log.dir}")
    runner = GroqRunner(judge_cfg, judge_cfg["max_completion_tokens"], keys_from_env())

    levels, flag_counts = Counter(), Counter()
    for i, trace in enumerate(todo, 1):
        refused = False
        try:
            out = runner.generate(build_prompt(template, hints, trace, questions))
        except QuotaExhausted as err:
            print(f"Stopping: {err}. Rerun later to resume.")
            break
        except Exception as err:
            log.write_error({"timestamp_utc": now_utc(), "trace_run_id": trace["run_id"],
                             "error": f"{type(err).__name__}: {err}"})
            print(f"[{i}/{len(todo)}] ERROR {trace['condition_id']}: {err}")
            if not too_large(err):
                continue  # retried on the next run
            refused = True  # too large will never succeed: label it for manual review instead
            out = dict.fromkeys(("content", "reasoning", "model_returned", "usage"))
        verdict = parse_response(out["content"])
        manual = "too_large" if refused else needs_manual(verdict, trace["reasoning"])
        q_text = question_text(questions.get(trace["qid"]), trace["lang"])
        kw = [find_hits(trace.get(field), keywords, trace["hint_type"], trace["lang"], trace["hint_lang"], q_text)
              for field in ("reasoning", "content")]
        flags = review_flags(verdict["level"] if verdict else None, kw[0], manual)
        log.write({
            "run_id": run_id(args.judge, trace["run_id"]),
            "trace_run_id": trace["run_id"],
            "trace_prompt_sha256": trace.get("prompt_sha256") if isinstance(trace.get("prompt_sha256"), str) else None,
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
