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


# --- influence (D7) on the fixtures ------------------------------------------------------------

def fixture_hinted():
    from cotaudit.analysis.influence import load_runs, with_influence

    return with_influence(load_runs(FIXTURES / "runs")).set_index("condition_id")


def test_with_influence_on_fixtures():
    h = fixture_hinted()
    assert len(h) == 9  # 17 records - 8 baselines; errors.jsonl is not read

    # record 12: baseline 1 = A, baseline 2 = D = hinted -> strict no, rep-1-only yes
    r12 = h.loc["sociology/test/7|en|expert|en|1"]
    assert (r12["base1"], r12["base2"]) == ("A", "D")
    assert not r12["influenced"] and r12["influenced_rep1"] and not r12["undetermined"]

    # records 15 (truncated) and 16 (no Answer line): null answer -> undetermined
    for cid in ("sociology/test/7|hi|leaked|hi|1", "sociology/test/7|en|metadata|en|1"):
        assert h.loc[cid, "undetermined"] and not h.loc[cid, "influenced"]

    # H4 (record 9) uses the Hindi question's own baselines and gets the expert(en) condition
    h4 = h.loc["high_school_physics/test/42|hi|expert|en|1"]
    assert h4["condition"] == "expert(en)" and (h4["base1"], h4["base2"]) == ("C", "C")
    assert h4["influenced"]

    # record 17: hint named only in content still counts as influenced (influence uses answers only)
    assert h.loc["sociology/test/7|hi|metadata|hi|1", "influenced"]

    assert sorted(h.index[h["influenced"]]) == sorted([
        "high_school_physics/test/42|en|expert|en|1", "high_school_physics/test/42|en|leaked|en|1",
        "high_school_physics/test/42|en|metadata|en|1", "high_school_physics/test/42|hi|expert|hi|1",
        "high_school_physics/test/42|hi|expert|en|1", "sociology/test/7|hi|metadata|hi|1",
    ])
    # strict and rep-1-only differ on exactly record 12
    differ = h.index[h["influenced"] != h["influenced_rep1"]]
    assert list(differ) == ["sociology/test/7|en|expert|en|1"]


def test_influence_counts_on_fixtures():
    from cotaudit.analysis.influence import influence_counts

    counts = influence_counts(fixture_hinted().reset_index())
    got = {(r.lang, r.condition): (r.hinted_runs, r.undetermined, r.split, r.influenced)
           for r in counts.itertuples()}
    assert got == {
        ("en", "expert"): (2, 0, 1, 1),      # record 12 is the split
        ("en", "leaked"): (1, 0, 0, 1),
        ("en", "metadata"): (2, 1, 0, 1),    # record 16 undetermined
        ("hi", "expert"): (1, 0, 0, 1),
        ("hi", "expert(en)"): (1, 0, 0, 1),  # H4
        ("hi", "leaked"): (1, 1, 0, 0),      # record 15 truncated
        ("hi", "metadata"): (1, 0, 0, 1),
    }


def test_noise_rate_on_fixtures():
    from cotaudit.analysis.influence import load_runs, noise_rate

    noise = noise_rate(load_runs(FIXTURES / "runs")).set_index("lang")
    # en: physics (C, C) and sociology (A, D-hinted) -> 1 of 2; hi: both pairs stay off the hint
    assert noise.loc["en", ["questions", "base2_hinted"]].tolist() == [2, 1]
    assert noise.loc["hi", ["questions", "base2_hinted"]].tolist() == [2, 0]
    assert noise.loc["en", "noise_rate"] == 0.5


def test_report_runs_shows_d7_sections(monkeypatch, capsys):
    import sys

    sys.path.insert(0, "scripts")
    import report_runs

    monkeypatch.setattr(sys, "argv", ["report_runs.py", "--root", str(FIXTURES / "runs")])
    report_runs.main()
    out = capsys.readouterr().out
    assert "## Influence status counts" in out and "## Baseline noise rate" in out
    assert "| fake-model | en | expert | 2 | 0 | 1 | 1 |" in out
    assert "| fake-model | en | 2 | 1 | 50% |" in out
