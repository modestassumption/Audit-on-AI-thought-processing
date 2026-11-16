"""Runs logged before the question set or a prompt changed: redo them, and leave them out of analysis."""

import argparse

from cotaudit.analysis.influence import load_runs
from cotaudit.runlog import RunLog, run_id
from cotaudit.runners.base import select_conditions

ARGS = argparse.Namespace(model="m", n_questions=None, langs=None, hint_types=None, no_h4=False,
                          limit=None, shard=None)


def cond(qid, sha):
    return {"condition_id": f"{qid}|hi|expert|hi|1", "qid": qid, "lang": "hi", "hint_type": "expert",
            "hint_lang": "hi", "prompt_sha256": sha}


def record(c, sha, ts="2026-11-10T00:00:00+00:00", answer="B"):
    return {"run_id": run_id("m", c["condition_id"]), "model": "m", "condition_id": c["condition_id"],
            "qid": c["qid"], "lang": "hi", "hint_type": "expert", "hint_lang": "hi", "rep": 1,
            "prompt_sha256": sha, "timestamp_utc": ts, "answer": answer}


def test_changed_prompt_is_run_again(tmp_path):
    log = RunLog("m", tmp_path, "t")
    same, changed, legacy, new = cond("q1", "s1"), cond("q2", "s2-new"), cond("q3", "s3"), cond("q4", "s4")
    log.write(record(same, "s1"))
    log.write(record(changed, "s2-old"))          # logged before the hint translation changed
    log.write({**record(legacy, None), "prompt_sha256": None})   # no hash: trust the id
    todo = select_conditions([same, changed, legacy, new], ARGS, log.completed_prompts())
    assert [c["qid"] for c in todo] == ["q2", "q4"]
    # the old id-only check would have skipped the changed prompt
    assert [c["qid"] for c in select_conditions([same, changed, legacy, new], ARGS, log.completed_ids())] == ["q4"]

    log.write(record(changed, "s2-new", ts="2026-11-20T00:00:00+00:00"))
    assert select_conditions([same, changed, legacy, new], ARGS, log.completed_prompts()) == [new]


def test_load_runs_leaves_out_dropped_and_stale_runs(tmp_path, capsys):
    log = RunLog("m", tmp_path, "t")
    kept, dropped, redone = cond("q1", "s1"), cond("q9", "s9"), cond("q2", "s2-new")
    log.write(record(kept, "s1"))
    log.write(record(dropped, "s9"))                                    # q9 left the dataset
    log.write(record(redone, "s2-old", answer="C"))                     # stale, logged first
    log.write(record(redone, "s2-new", ts="2026-11-20T00:00:00+00:00", answer="B"))
    current = {kept["condition_id"]: "s1", redone["condition_id"]: "s2-new"}

    df = load_runs(tmp_path, current=current)
    assert sorted(df["qid"]) == ["q1", "q2"]
    assert df.set_index("qid").loc["q2", "answer"] == "B"              # the redone run, not the stale one
    assert "left out 2 runs" in capsys.readouterr().err

    # folders other than runs/ (test fixtures, smoke runs) are not filtered unless asked
    assert len(load_runs(tmp_path)) == 3                               # duplicates of q2 still collapse
