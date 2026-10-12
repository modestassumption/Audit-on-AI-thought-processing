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
    args = argparse.Namespace(model="m", n_questions=None, langs=None, hint_types=None, no_h4=False, limit=None)
    todo = select_conditions(conds, args, log.completed_ids())
    assert [c["qid"] for c in todo] == ["q1", "q2"]
