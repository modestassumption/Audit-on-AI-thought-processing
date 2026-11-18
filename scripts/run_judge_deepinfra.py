"""Judge influenced traces with gpt-oss-120b served by DeepInfra instead of Groq, resuming where it left off.

    python scripts/run_judge_deepinfra.py --models r1-distill-llama-8b --limit 3
    python scripts/run_judge_deepinfra.py --models r1-distill-llama-8b

Same judge model, prompt, parsing, keyword hits, flags, judging order and resume rule as
run_judge.py (imported from it unchanged); only the API differs. Used for the R1-Distill traces
on 2026-11-18, when every Groq free-tier key had hit its 200K tokens-per-day cap on gpt-oss-120b.

Every label records `provider: "deepinfra"` and the DeepInfra model id, and goes to
labels/gpt-oss-120b/<date>-<tag>.jsonl (default tag `sanjay-deepinfra`), so DeepInfra labels are
never mistaken for Groq ones. The key is read from the environment variable named by --key-env
(default DEEPINFRA_API_KEY; .env is loaded first). Stops when DeepInfra reports no credit left.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from dotenv import load_dotenv

from cotaudit.analysis.influence import label_is_current
from cotaudit.config import LABELS, load_experiment, load_hints
from cotaudit.judge.keywords import find_hits, load_keywords, load_questions, question_text, review_flags
from cotaudit.judge.llm_judge import build_prompt, load_template, needs_manual, parse_response
from cotaudit.runlog import RunLog, now_utc, run_id

URL = "https://api.deepinfra.com/v1/openai/chat/completions"
PROVIDER = "deepinfra"
JUDGE = "gpt-oss-120b"


def _load_run_judge():
    """run_judge.py is a script, not a module: load it to reuse targets/order/labels unchanged."""
    path = Path(__file__).with_name("run_judge.py")
    spec = importlib.util.spec_from_file_location("run_judge", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class OutOfCredit(RuntimeError):
    pass


def call(client: httpx.Client, key: str, payload: dict, attempts: int = 6) -> dict:
    """One chat completion; retries rate limits and server errors with backoff."""
    for i in range(attempts):
        try:
            r = client.post(URL, headers={"Authorization": f"Bearer {key}"}, json=payload)
        except httpx.TransportError:
            time.sleep(min(60, 2 ** (i + 1)))
            continue
        if r.status_code == 402:
            raise OutOfCredit(r.text[:200])
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(60, 2 ** (i + 1)))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"DeepInfra request failed {attempts} times")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", help="only traces from these models")
    ap.add_argument("--limit", type=int, help="stop after this many new labels")
    ap.add_argument("--tag", default="sanjay-deepinfra", help="log file suffix")
    ap.add_argument("--key-env", default="DEEPINFRA_API_KEY", help="environment variable holding the DeepInfra key")
    ap.add_argument("--model-id", default="openai/gpt-oss-120b", help="DeepInfra model id")
    ap.add_argument("--workers", type=int, default=8, help="requests in flight at once (labels are still written one at a time)")
    args = ap.parse_args()

    load_dotenv(".env")
    key = (os.environ.get(args.key_env) or "").strip()
    if not key:
        raise SystemExit(f"{args.key_env} is not set")

    rj = _load_run_judge()
    cfg, hints, keywords, template = load_experiment(), load_hints(), load_keywords(), load_template()
    questions = load_questions()
    judge_cfg = cfg["judges"][JUDGE]
    params = {"temperature": judge_cfg["temperature"], "top_p": judge_cfg["top_p"],
              "max_completion_tokens": judge_cfg["max_completion_tokens"],
              "reasoning_effort": judge_cfg.get("reasoning_effort")}
    log = RunLog(JUDGE, LABELS, args.tag)

    sel = argparse.Namespace(models=args.models, all_hinted=False, shard=None, key=None)
    traces = rj.targets(sel)
    by_id = {t["run_id"]: t for t in traces}
    done = {lab["trace_run_id"] for lab in rj.read_labels(JUDGE)
            if label_is_current(lab, by_id.get(lab.get("trace_run_id")))}
    todo = [t for t in rj.judge_order(traces, cfg["seed"]) if t["run_id"] not in done]
    todo = todo[: args.limit] if args.limit else todo
    print(f"{JUDGE} on {PROVIDER}: {len(todo)} traces to label -> {log.dir}")

    def request(trace: dict) -> tuple[dict | None, float, Exception | None]:
        payload = {"model": args.model_id,
                   "messages": [{"role": "user", "content": build_prompt(template, hints, trace, questions)}],
                   "temperature": params["temperature"], "top_p": params["top_p"],
                   "max_tokens": params["max_completion_tokens"],
                   "reasoning_effort": params["reasoning_effort"]}
        start = time.time()
        try:
            return call(client, key, payload), round(time.time() - start, 2), None
        except Exception as err:  # noqa: BLE001
            return None, round(time.time() - start, 2), err

    levels = Counter()
    with httpx.Client(timeout=300) as client, ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = pool.map(request, todo)   # in judging order; only this thread writes labels
        for i, (trace, (resp, latency, err)) in enumerate(zip(todo, results), 1):
            if isinstance(err, OutOfCredit):
                print(f"Stopping: DeepInfra reports no credit left ({err}). Rerun after topping up.")
                pool.shutdown(wait=False, cancel_futures=True)
                break
            if err is not None:
                log.write_error({"timestamp_utc": now_utc(), "trace_run_id": trace["run_id"],
                                 "provider": PROVIDER, "error": f"{type(err).__name__}: {err}"})
                print(f"[{i}/{len(todo)}] ERROR {trace['condition_id']}: {err}")
                continue
            msg = resp["choices"][0]["message"]
            content = msg.get("content")
            verdict = parse_response(content)
            manual = needs_manual(verdict, trace["reasoning"])
            q_text = question_text(questions.get(trace["qid"]), trace["lang"])
            kw = [find_hits(trace.get(field), keywords, trace["hint_type"], trace["lang"], trace["hint_lang"], q_text)
                  for field in ("reasoning", "content")]
            flags = review_flags(verdict["level"] if verdict else None, kw[0], manual)
            log.write({
                "run_id": run_id(JUDGE, trace["run_id"]),
                "trace_run_id": trace["run_id"],
                "trace_prompt_sha256": trace.get("prompt_sha256") if isinstance(trace.get("prompt_sha256"), str) else None,
                "judge": JUDGE,
                "judge_model_id": judge_cfg["model_id"],
                "provider": PROVIDER,
                "provider_model_id": args.model_id,
                "timestamp_utc": now_utc(),
                "params": params,
                **{k: trace[k] for k in rj.TRACE_FIELDS},
                "influenced": bool(trace["influenced"]),
                "level": verdict["level"] if verdict else None,
                "quote": verdict["quote"] if verdict else None,
                "restate_only": verdict["restate_only"] if verdict else None,
                "rationale": verdict["rationale"] if verdict else None,
                "needs_manual": manual,
                "kw_hits": kw[0],
                "content_kw_hits": kw[1],
                "flags": flags,
                "judge_content": content,
                "judge_reasoning": msg.get("reasoning_content") or msg.get("reasoning"),
                "model_returned": resp.get("model"),
                "usage": resp.get("usage"),
                "latency_s": latency,
            })
            levels[verdict["level"] if verdict else "?"] += 1
            print(f"[{i}/{len(todo)}] {trace['model']} {trace['condition_id']} -> level "
                  f"{verdict['level'] if verdict else '?'}{' (manual: ' + manual + ')' if manual else ''}")

    print(f"Done: levels {dict(levels)}")


if __name__ == "__main__":
    main()
