"""The hand-written run-log fixtures stay in the real run-log format and cover every labelling case."""

from __future__ import annotations

import json
from pathlib import Path

from cotaudit.extract import extract_answer
from cotaudit.runlog import run_id
from cotaudit.runners.base import CONDITION_FIELDS

FIXTURES = Path(__file__).parent / "fixtures"
FAKE_LOG = FIXTURES / "runs" / "fake-model" / "2026-01-01.jsonl"

REQUIRED = (
    "run_id", "model", "model_id", "provider", "timestamp_utc", "params",
    "reasoning", "content", "answer", "finish_reason", "usage", *CONDITION_FIELDS,
)


def records() -> list[dict]:
    lines = FAKE_LOG.read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def test_fixture_records_match_the_run_log_format():
    recs = records()
    assert len(recs) == 17
    for rec in recs:
        assert not set(REQUIRED) - set(rec), rec["condition_id"]
        assert rec["run_id"] == run_id(rec["model"], rec["condition_id"])
        assert rec["answer"] == extract_answer(rec["content"])
        hint_lang = rec["hint_lang"] or "-"
        assert rec["condition_id"] == "|".join(
            [rec["qid"], rec["lang"], rec["hint_type"], hint_lang, str(rec["rep"])]
        )
        # the filename RunLog.write would choose
        assert rec["timestamp_utc"][:10] == FAKE_LOG.stem


def test_fixture_covers_the_required_cases():
    by_cid = {r["condition_id"]: r for r in records()}
    langs = {r["lang"] for r in by_cid.values()}
    assert langs == {"en", "hi"}
    assert len({r["qid"] for r in by_cid.values()}) == 2

    # H4: English hint inside a Hindi question
    h4 = [r for r in by_cid.values() if r["hint_lang"] == "en" and r["lang"] != "en"]
    assert len(h4) == 1 and h4[0]["hint_type"] == "expert"

    # two baselines per (qid, lang)
    for qid in {r["qid"] for r in by_cid.values()}:
        for lang in langs:
            reps = sorted(r["rep"] for r in by_cid.values()
                          if r["qid"] == qid and r["lang"] == lang and r["hint_type"] == "none")
            assert reps == [1, 2]

    truncated = [r for r in by_cid.values() if r["finish_reason"] == "length"]
    assert len(truncated) == 1 and truncated[0]["answer"] is None

    nulls = [r for r in by_cid.values() if r["answer"] is None]
    assert len(nulls) == 2  # one truncated, one that simply never wrote "Answer: X"

    # hint named in `content` only
    only_content = by_cid["sociology/test/7|hi|metadata|hi|1"]
    assert "मेटाडेटा" in only_content["content"]
    assert "मेटाडेटा" not in only_content["reasoning"]

    # exactly one baseline on the hinted letter, which is what strict/lenient disagree about
    picked = [r["answer"] for r in by_cid.values()
              if r["qid"] == "sociology/test/7" and r["lang"] == "en" and r["hint_type"] == "none"]
    assert sorted(picked) == ["A", "D"]


def test_errors_file_is_separate_from_the_run_records():
    errors = (FAKE_LOG.parent / "errors.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(errors) == 1
    assert "run_id" not in json.loads(errors[0])
