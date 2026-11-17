import csv
import sys

from cotaudit.analysis.influence import load_runs
from cotaudit.runlog import RunLog


def fake_runs(root):
    """r1-style log: Answer: X, boxed, a cut-off run, a conflict, and one logged by an older extractor."""
    log = RunLog("r1-distill-llama-8b", root, "t")
    base = {"model": "r1-distill-llama-8b", "subject": "anatomy", "stratum": "stem", "gold": "C",
            "hinted": "B", "hint_type": "none", "hint_lang": None, "rep": 1, "reasoning": "x",
            "finish_reason": "stop", "think_closed": True, "timestamp_utc": "2026-11-16T00:00:00+00:00"}
    rows = [
        ("en", "Answer: C", "C", {}),
        ("en", "**Final Answer**\n\\boxed{B}", "B", {}),
        ("en", "", None, {"finish_reason": "length", "think_closed": False}),
        ("hi", "Answer: A\n\nWait, no.\n\nAnswer: C", "C", {}),
        ("zh", "答案：C选项", None, {}),          # logged before the CJK fix
        ("zh", "I cannot tell.", None, {}),
        ("ml", "ĊĊTheĠcorrectĠanswerĠisĠD.", None, {}),   # tokenizer not applied on decode
    ]
    for i, (lang, content, logged, extra) in enumerate(rows):
        log.write({**base, "run_id": f"r{i}", "condition_id": f"c{i}", "qid": f"anatomy/test/{i}",
                   "lang": lang, "content": content, "answer": logged, **extra})


def test_check_extraction_summary_and_files(tmp_path):
    sys.path.insert(0, "scripts")
    import check_extraction as ce

    fake_runs(tmp_path / "runs")
    df = ce.recheck(load_runs(tmp_path / "runs"))
    cells = {r["lang"]: r for r in ce.summary(df)}

    assert cells["en"]["runs"] == 3
    assert cells["en"]["extracted"] == "67%"
    assert cells["en"]["cut off"] == "33%"
    assert cells["en"]["via label"] == "33%" and cells["en"]["via boxed"] == "33%"
    assert cells["hi"]["conflicting letters"] == 1
    assert cells["zh"]["logged differs"] == 1      # stale "None" -> "C" under the current extractor
    assert cells["ml"]["undecoded tokens"] == 1 and cells["en"]["undecoded tokens"] == 0

    bad = df[df["extracted"].isna() | (df["candidates"].str.len() > 1)]
    assert set(bad["run_id"]) == {"r2", "r3", "r5", "r6"}

    rows = ce.sample_rows(df, per_cell=1, seed=0)
    assert {r["lang"] for r in rows} == {"en", "hi", "zh"}   # the ml run has no letter to check
    path = tmp_path / "hand_check.csv"
    ce.write_csv(path, rows, extra=["hand_answer"])
    with open(path, encoding="utf-8-sig", newline="") as f:
        filled = list(csv.DictReader(f))
    for r in filled:
        r["hand_answer"] = r["extracted"]
    filled[0]["hand_answer"] = "D"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filled[0]))
        w.writeheader()
        w.writerows(filled)
    report = ce.score(path)
    assert "Overall: 2/3" in report
    assert "hand D" in report
