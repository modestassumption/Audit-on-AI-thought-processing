import json
from collections import Counter

from cotaudit.conditions import build_conditions, condition_specs
from cotaudit.config import DATA, load_experiment, load_hints

CFG, HINTS = load_experiment(), load_hints()
QUESTIONS = [json.loads(ln) for ln in (DATA / "questions.jsonl").read_text(encoding="utf-8").splitlines()]


def test_23_specs_per_question():
    specs = condition_specs(CFG)
    assert len(specs) == 23
    h4 = [s for s in specs if s["hint_type"] != "none" and s["hint_lang"] != s["lang"]]
    assert len(h4) == 3 and all(s["lang"] != "en" and s["hint_lang"] == "en" for s in h4)


def test_full_grid_is_6900_with_unique_ids():
    rows = build_conditions(QUESTIONS, CFG, HINTS)
    assert len(rows) == 6900
    assert len({r["condition_id"] for r in rows}) == 6900
    kinds = Counter(
        "base" if r["hint_type"] == "none" else "h4" if r["hint_lang"] != r["lang"] else "hint"
        for r in rows
    )
    assert kinds == {"base": 2400, "hint": 3600, "h4": 900}


def test_dataset_shape():
    assert len(QUESTIONS) == 300
    assert Counter(q["stratum"] for q in QUESTIONS) == {"stem": 150, "humanities": 150}
    for q in QUESTIONS:
        assert q["hinted"] != q["gold"]
        assert set(q["text"]) == {"en", "hi", "zh", "ml"}
        assert all(len(t["options"]) == 4 for t in q["text"].values())


def test_every_subject_has_a_name_in_every_language():
    for lang, entry in HINTS["subjects"].items():
        missing = {q["subject"] for q in QUESTIONS} - set(entry["names"])
        assert not missing, (lang, missing)
