import pytest

from cotaudit.extract import extract_answer
from cotaudit.runners.vllm_runner import split_think


@pytest.mark.parametrize("text,expected", [
    ("Reasoning...\nAnswer: C", "C"),
    ("**Answer:** (B)", "B"),
    ("Answer: A\n...wait\nAnswer: D", "D"),
    ("答案：B", "B"),
    ("अंतिम उत्तर: A", "A"),
    ("ഉത്തരം: D", "D"),
    ("so \\boxed{C}", "C"),
    ("Thus the answer is (D).", "D"),
    ("(B)", "B"),
    ("I am not sure.", None),
    ("", None),
    (None, None),
    ("Answer: E", None),
])
def test_extract_answer(text, expected):
    assert extract_answer(text) == expected


def test_split_think():
    assert split_think("<think>\nhmm\n</think>\n\nAnswer: B") == ("hmm", "Answer: B", True)
    assert split_think("hmm</think>Answer: A") == ("hmm", "Answer: A", True)
    assert split_think("<think>\nstill going") == ("still going", "", False)
