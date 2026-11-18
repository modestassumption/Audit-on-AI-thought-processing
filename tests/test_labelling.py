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
    for mod in (export_labelling, agreement):
        monkeypatch.setattr(mod, "RUNS", runs)
    questions = {f"anatomy/test/{i}": {"text": {"en": {"question": f"Question {i}?", "options": ["w", "x", "y", "z"]}}}
                 for i in range(6)}
    monkeypatch.setattr(export_labelling, "load_questions", lambda: questions)
    monkeypatch.setattr(sys, "argv", ["x", "--name", "p", "--per-cell", "4"])
    export_labelling.main()

    folder = labels / "human" / "p"
    items = pd.read_csv(folder / "items.csv", encoding="utf-8-sig")
    assert len(items) == 8
    assert "model" not in items.columns and "gold" not in items.columns
    assert {"question", "options", "level", "restate_only"} <= set(items.columns)
    assert items["question"].str.match(r"Question \d\?").all()
    assert (items["options"] == "(A) w\n(B) x\n(C) y\n(D) z").all()
    assert items["hint_text"].str.contains("unauthorized access").all()

    for name, levels in (("alice", [2, 2, 0, 1, 2, 0, 1, 2]), ("bob", [2, 2, 0, 1, 2, 0, 0, 2])):
        items.assign(level=levels, restate_only="yes").to_csv(folder / f"{name}.csv", index=False, encoding="utf-8-sig")
    monkeypatch.setattr(sys, "argv", ["x", "--name", "p"])
    agreement.main()
    out = capsys.readouterr().out
    assert "alice vs bob" in out
    table = pd.read_csv(folder / "agreement.csv", encoding="utf-8-sig")
    pooled = table[(table["slice"] == "pooled") & (table["measure"] == "main (2 vs 0/1)")].iloc[0]
    assert pooled["n"] == 8 and pooled["pct_agree"] == 100.0 and pooled["kappa"] == 1.0
    assert set(table["slice"]) == {"pooled", "group: direct (en+hi)", "lang: en", "model: m1", "model: m2"}
    agreement.main()  # a second run must not read agreement.csv as a labeller
    assert len(pd.read_csv(folder / "agreement.csv", encoding="utf-8-sig")) == len(table)

    # One exported trace is re-run after export: its human labels describe text that no longer
    # exists, so the item leaves every pair instead of being compared with a judge on new text.
    run_id = pd.read_csv(folder / "key.csv", encoding="utf-8-sig")["run_id"].iloc[0]
    model, i = run_id[:2], run_id[2:-1]
    log = next((runs / model).glob("20*.jsonl"))
    log.write_text(log.read_text(encoding="utf-8").replace(f'"trace {model} {i}"', '"re-run text"'),
                   encoding="utf-8")
    capsys.readouterr()
    agreement.main()
    assert "1 items whose trace was re-run after export" in capsys.readouterr().err
    table = pd.read_csv(folder / "agreement.csv", encoding="utf-8-sig")
    pooled = table[(table["slice"] == "pooled") & (table["measure"] == "main (2 vs 0/1)")].iloc[0]
    assert pooled["n"] == 7 and pooled["excluded"] == 0


def test_bootstrap_interval_is_seeded_and_drops_undefined_resamples():
    from cotaudit.analysis.agreement import agreement_stats, bootstrap_kappa

    a = [1] * 25 + [0] * 25
    b = [1] * 20 + [0] * 5 + [1] * 10 + [0] * 15            # kappa 0.40
    low, high, dropped = bootstrap_kappa(a, b, seed=21)
    assert low < 0.40 < high and 0.1 < low and high < 0.7 and dropped == 0
    assert bootstrap_kappa(a, b, seed=21) == (low, high, dropped)
    assert bootstrap_kappa(a, b, seed=22) != (low, high, dropped)

    # one disagreement among 6: resamples that miss it leave a single class and are dropped
    low, high, dropped = bootstrap_kappa([0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0], seed=21, n_boot=1000)
    assert 250 < dropped < 450                               # (5/6)^6 = 33.5% of resamples
    low, high, dropped = bootstrap_kappa([2, 2, 2], [2, 2, 2], seed=21, n_boot=50)
    assert dropped == 50 and low != low and high != high     # all undefined: nan interval

    stats = agreement_stats(a, b, seed=21)
    assert stats["n"] == 50 and stats["pct_agree"] == 70.0 and stats["kappa"] == 0.4
    assert stats["prev_a"] == "0:0.50 1:0.50" and stats["prev_b"] == "0:0.40 1:0.60"
    assert stats["ci_low"] < 0.4 < stats["ci_high"] and stats["boot_dropped"] == 0


def test_agreement_table_slices_groups_and_the_judge_own_traces():
    sys.path.insert(0, "scripts")
    import agreement

    rows = [(f"i{n:02d}", model, lang) for n, (model, lang) in enumerate(
        (m, lang) for m in ("qwen3.8-27b", "gpt-oss-20b") for lang in ("en", "hi", "zh", "ml") for _ in range(3))]
    key = pd.DataFrame(rows, columns=["item_id", "model", "lang"]).set_index("item_id")
    human = pd.Series([2.0, 1.0, 0.0] * 8, index=key.index)
    human.iloc[0] = float("nan")                              # one item marked exclude
    judge = pd.Series([2.0, 0.0, 0.0] * 8, index=key.index).drop("i23")   # one trace never judged
    table = agreement.agreement_table(key, {"adjudicated": human, "judge:qwen3.8-27b": judge}, seed=21, n_boot=200)

    assert set(table["pair"]) == {"adjudicated vs judge:qwen3.8-27b"} and len(table) == 11 * 3
    main = table[table["measure"] == "main (2 vs 0/1)"].set_index("slice")
    assert main.loc["pooled", ["n", "excluded"]].tolist() == [22, 2]
    assert main.loc["group: direct (en+hi)", "n"] == 11 and main.loc["group: translation-mediated (zh+ml)", "n"] == 11
    assert main.loc["lang: en", ["n", "excluded"]].tolist() == [5, 1]
    assert main.loc["qwen3.8-27b own traces", "n"] == 11 and main.loc["qwen3.8-27b other models' traces", "n"] == 11
    assert main.loc["pooled", "kappa"] == 1.0                 # level 2 is never disputed here
    loose = table[(table["measure"] == "loose (1/2 vs 0)") & (table["slice"] == "pooled")].iloc[0]
    assert loose["kappa"] < 1 and loose["ci_low"] <= loose["kappa"] <= loose["ci_high"]

    humans = agreement.agreement_table(key, {"a": human, "b": human}, seed=21, n_boot=50)
    assert not humans["slice"].str.contains("own traces").any()   # the split is for the judge only
