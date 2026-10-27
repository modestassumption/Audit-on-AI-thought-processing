import sys

import pandas as pd
import pytest

from cotaudit.analysis.agreement import cohen_kappa
from cotaudit.runlog import RunLog


def test_cohen_kappa_known_values():
    assert cohen_kappa([0, 1, 2, 2], [0, 1, 2, 2]) == 1.0
    # 2x2 table [[20, 5], [10, 15]]: po = 0.70, pe = 0.50 -> kappa 0.40
    a = [1] * 25 + [0] * 25
    b = [1] * 20 + [0] * 5 + [1] * 10 + [0] * 15
    assert cohen_kappa(a, b) == pytest.approx(0.40)
    with pytest.raises(ValueError):
        cohen_kappa([1], [1, 2])


def test_export_is_blinded_and_agreement_runs(tmp_path, monkeypatch, capsys):
    sys.path.insert(0, "scripts")
    import agreement
    import export_labelling

    runs, labels = tmp_path / "runs", tmp_path / "labels"
    for model in ("m1", "m2"):
        log = RunLog(model, runs, "t")
        for i in range(6):
            base = {"model": model, "qid": f"anatomy/test/{i}", "subject": "anatomy", "stratum": "stem",
                    "lang": "en", "gold": "C", "hinted": "B", "finish_reason": "stop",
                    "timestamp_utc": "2026-10-28T00:00:00+00:00"}
            for rep in (1, 2):
                log.write({**base, "run_id": f"{model}{i}b{rep}", "condition_id": f"{i}b{rep}",
                           "hint_type": "none", "hint_lang": None, "rep": rep, "answer": "C", "reasoning": "x"})
            log.write({**base, "run_id": f"{model}{i}h", "condition_id": f"{i}h", "hint_type": "leaked",
                       "hint_lang": "en", "rep": 1, "answer": "B", "reasoning": f"trace {model} {i}"})

    for mod in (export_labelling, agreement):
        monkeypatch.setattr(mod, "LABELS", labels)
    monkeypatch.setattr(export_labelling, "RUNS", runs)
    monkeypatch.setattr(sys, "argv", ["x", "--name", "p", "--per-cell", "4"])
    export_labelling.main()

    folder = labels / "human" / "p"
    items = pd.read_csv(folder / "items.csv", encoding="utf-8-sig")
    assert len(items) == 8
    assert "model" not in items.columns and "level" in items.columns
    assert items["hint_text"].str.contains("unauthorized access").all()

    for name, levels in (("alice", [2, 2, 0, 1, 2, 0, 1, 2]), ("bob", [2, 2, 0, 1, 2, 0, 0, 2])):
        items.assign(level=levels).to_csv(folder / f"{name}.csv", index=False, encoding="utf-8-sig")
    monkeypatch.setattr(sys, "argv", ["x", "--name", "p"])
    agreement.main()
    out = capsys.readouterr().out
    assert "alice vs bob" in out and "  8 " in out
