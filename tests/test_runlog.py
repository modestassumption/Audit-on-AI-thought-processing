import argparse

from cotaudit.runlog import RunLog, now_utc, run_id
from cotaudit.runners.base import select_conditions


def test_run_id_depends_on_model_and_condition():
    assert run_id("m", "c") == run_id("m", "c")
    assert run_id("m", "c") != run_id("m2", "c")


def test_resume_skips_logged_runs_but_retries_errors(tmp_path):
    log = RunLog("m", tmp_path)
    conds = [
        {"condition_id": f"q{i}|en|none|-|1", "qid": f"q{i}", "lang": "en", "hint_type": "none", "hint_lang": None}
        for i in range(3)
    ]
    log.write({"run_id": run_id("m", conds[0]["condition_id"]), "timestamp_utc": now_utc()})
    log.write_error({"condition_id": conds[1]["condition_id"], "error": "boom"})
    args = argparse.Namespace(model="m", n_questions=None, langs=None, hint_types=None, no_h4=False, limit=None, shard=None)
    todo = select_conditions(conds, args, log.completed_ids())
    assert [c["qid"] for c in todo] == ["q1", "q2"]


def test_pilot_subset_is_balanced_and_shards_are_disjoint():
    import json
    from cotaudit.config import DATA

    rows = [json.loads(ln) for ln in (DATA / "conditions.jsonl").read_text(encoding="utf-8").splitlines()]
    base = dict(model="m", langs=None, hint_types=None, no_h4=False, limit=None, shard=None)
    pilot = select_conditions(rows, argparse.Namespace(**base, n_questions=50), set(), seed=21)
    qids = {r["qid"]: r["stratum"] for r in pilot}
    assert len(qids) == 50 and sum(s == "stem" for s in qids.values()) == 25
    assert len(pilot) == 50 * 23
    parts = [select_conditions(rows, argparse.Namespace(**{**base, "shard": (i, 3)}, n_questions=50), set(), seed=21)
             for i in (1, 2, 3)]
    assert sum(len(p) for p in parts) == len(pilot)


def test_logs_are_tagged_per_member(tmp_path):
    a, b = RunLog("m", tmp_path, "alice"), RunLog("m", tmp_path, "bob")
    a.write({"run_id": "1", "timestamp_utc": "2026-10-28T00:00:00+00:00"})
    b.write({"run_id": "2", "timestamp_utc": "2026-10-28T00:00:00+00:00"})
    assert sorted(p.name for p in (tmp_path / "m").iterdir()) == ["2026-10-28-alice.jsonl", "2026-10-28-bob.jsonl"]
    assert RunLog("m", tmp_path, "carol").completed_ids() == {"1", "2"}
