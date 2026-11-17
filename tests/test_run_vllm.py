import sys

import pytest

from cotaudit.runlog import RunLog


class FakeRunner:
    """Stands in for VLLMRunner (no GPU): R1-style output with the </think> split already done."""
    def __init__(self, model_cfg, max_tokens, tp, dtype, seed, **engine_args):
        self.engine_args = engine_args
        self.params = {"temperature": 0.6, "top_p": 0.95, "max_completion_tokens": max_tokens}
        FakeRunner.last = self

    def generate_batch(self, prompts):
        return [{"model_returned": "fake", "reasoning": "hmm", "content": "**Final Answer**\n\\boxed{B}",
                 "think_closed": True, "finish_reason": "stop", "usage": {}, "latency_s": 0.0,
                 "key_alias": None} for _ in prompts]


def conditions(n):
    return [{"condition_id": f"c{i}", "qid": f"anatomy/test/{i}", "subject": "anatomy", "stratum": "stem",
             "lang": "en", "hint_type": "none", "hint_lang": None, "rep": 1, "gold": "C", "hinted": "B",
             "prompt_sha256": "x", "prompt": f"question {i}"} for i in range(n)]


@pytest.fixture
def run_vllm(tmp_path, monkeypatch):
    sys.path.insert(0, "scripts")
    import run_vllm as rv

    monkeypatch.setattr(rv, "VLLMRunner", FakeRunner)
    monkeypatch.setattr(rv, "load_conditions", lambda: conditions(5))
    monkeypatch.setattr(rv, "RunLog", lambda model, tag=None: RunLog(model, tmp_path, tag or "t"))
    return rv, tmp_path


def run(rv, monkeypatch, *flags):
    monkeypatch.setattr(sys, "argv", ["run_vllm.py", "--model", "r1-distill-llama-8b", "--tp", "2",
                                      "--batch-size", "2", *flags])
    rv.main()


def test_logs_every_run_and_resumes(run_vllm, monkeypatch, capsys):
    rv, root = run_vllm
    run(rv, monkeypatch, "--gpu-memory-utilization", "0.85", "--enforce-eager")
    assert FakeRunner.last.engine_args == {"gpu_memory_utilization": 0.85, "enforce_eager": True}
    log = RunLog("r1-distill-llama-8b", root, "t")
    assert len(log.completed_ids()) == 5
    records = [ln for p in log.dir.glob("20*.jsonl") for ln in p.read_text(encoding="utf-8").splitlines()]
    assert all('"answer": "B"' in r for r in records)     # boxed answer extracted
    run(rv, monkeypatch)                                   # second call: nothing left to do
    assert "0 runs to do" in capsys.readouterr().out


def test_max_hours_stops_before_next_batch(run_vllm, monkeypatch, capsys):
    rv, root = run_vllm
    # Windows' clock can return the same time twice in a row, so give the script one that always advances.
    import itertools
    import types
    monkeypatch.setattr(rv, "time", types.SimpleNamespace(time=itertools.count(0.0, 1.0).__next__))
    run(rv, monkeypatch, "--max-hours", "1e-9")
    assert RunLog("r1-distill-llama-8b", root, "t").completed_ids() == set()
    out = capsys.readouterr().out
    assert "--max-hours 1e-09 reached" in out and "0 runs, 5 left" in out


def test_tokenizer_round_trip_check():
    from cotaudit.runners.vllm_runner import CHECK_TEXTS, check_round_trip, decode_output

    good_enc = lambda s: list(s.encode("utf-8"))                       # noqa: E731
    good_dec = lambda ids: bytes(ids).decode("utf-8")                  # noqa: E731
    check_round_trip(good_enc, good_dec)

    # what Kaggle's tokenizer did on 2026-11-16: non-ASCII text dropped, spaces left as "Ġ"
    broken_enc = lambda s: [ord(c) for c in s if ord(c) < 128]         # noqa: E731
    broken_dec = lambda ids: "".join("Ġ" if i == 32 else chr(i) for i in ids)  # noqa: E731
    with pytest.raises(RuntimeError, match="round trip failed for en"):
        check_round_trip(broken_enc, broken_dec)
    with pytest.raises(RuntimeError, match="round trip failed for hi"):
        check_round_trip(broken_enc, lambda ids: "".join(map(chr, ids)), {"hi": CHECK_TEXTS["hi"]})

    assert decode_output(good_dec, list("Answer: B<｜end▁of▁sentence｜>".encode())) == "Answer: B"
