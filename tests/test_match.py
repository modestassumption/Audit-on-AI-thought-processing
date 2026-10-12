import pytest

from cotaudit.data.match import match_sarvam_to_mmlu, normalise


def row(q, opts, ans, **kw):
    return {"question": q, "options": opts, "answer": ans, **kw}


MMLU = [
    row("What is 2+2?", ["3", "4", "5", "6"], "B", sample_id="math/test/0"),
    row("Capital of France?", ["Paris", "Rome", "Oslo", "Bern"], "A", sample_id="geo/test/0"),
    row("Dup?", ["a", "b", "c", "d"], "A", sample_id="x/test/0"),
    row("Dup?", ["a", "b", "c", "d"], "A", sample_id="x/test/1"),
]


def test_normalise_ignores_case_punctuation_and_spacing():
    assert normalise("What  is 2+2 ?") == normalise("what is 2 + 2?")


def test_matches_through_row_aligned_english():
    en = [row("capital of france", ["Paris", "Rome", "Oslo", "Bern"], "A", row=0),
          row("What is 2 + 2?", ["3", "4", "5", "6"], "B", row=1)]
    ml = [row("ml-france", ["p", "r", "o", "b"], "A", row=0),
          row("ml-sum", ["3", "4", "5", "6"], "B", row=1)]
    out = match_sarvam_to_mmlu(MMLU, en, ml)
    assert out["geo/test/0"]["question"] == "ml-france"
    assert out["math/test/0"]["question"] == "ml-sum"


def test_drops_answer_disagreement_and_ambiguous_text():
    en = [row("What is 2+2?", ["3", "4", "5", "6"], "B", row=0),
          row("Dup?", ["a", "b", "c", "d"], "A", row=1)]
    ml = [row("ml", ["3", "4", "5", "6"], "C", row=0),
          row("ml-dup", ["a", "b", "c", "d"], "A", row=1)]
    assert match_sarvam_to_mmlu(MMLU, en, ml) == {}


def test_rejects_misaligned_configs():
    with pytest.raises(ValueError):
        match_sarvam_to_mmlu(MMLU, [row("a", [], "A")], [])
