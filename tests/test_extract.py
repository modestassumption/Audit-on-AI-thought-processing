import pytest

from cotaudit.extract import candidate_letters, extract_answer, extract_with_rule
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


@pytest.mark.parametrize("text,expected", [
    # lower-case words are not option letters
    ("Honestly the answer is a bit unclear.", None),
    ("The answer is a matter of definition. Answer: C", "C"),
    ("Answer: because of osmosis", None),
    # ... unless bracketed
    ("Answer: (c)", "C"),
    # a letter followed by CJK text (no \b between C and 选)
    ("答案：C选项", "C"),
    ("最终答案是 C。", "C"),
    # full-width letters, colons and brackets
    ("答案：Ｃ", "C"),
    ("Answer：（Ｂ）", "B"),
    # markdown and LaTeX wrappers
    ("**Answer: D**", "D"),
    ("Answer: **A**", "A"),
    ("Final Answer: $B$", "B"),
    ("Answer: (C) Mitochondria", "C"),
    ("**Final Answer**\n\\boxed{B}", "B"),
    ("\\boxed{\\text{D}}", "D"),
    ("\\boxed{(A)}", "A"),
    ("\\boxed{C. Mitochondria}", "C"),
    # answers in the question's language
    ("सही उत्तर (B) है।", "B"),
    ("इसलिए उत्तर है: D", "D"),
    ("ശരിയായ ഉത്തരം (A) ആണ്.", "A"),
    ("所以答案为B", "B"),
    ("我选C。", "C"),
    ("The correct option is D.", "D"),
    # the instruction's template echoed back is not an answer
    ('Answer: X', None),
    ("**C**", "C"),
])
def test_extract_answer_formats(text, expected):
    assert extract_answer(text) == expected


def test_label_beats_boxed_and_phrase():
    assert extract_with_rule("the answer is (B)\n\\boxed{B}\nAnswer: B") == ("B", "label")
    assert extract_with_rule("Thus \\boxed{C}") == ("C", "boxed")
    assert extract_with_rule("Thus the answer is C") == ("C", "phrase")
    assert extract_with_rule("...\nD") == ("D", "bare")
    assert extract_with_rule("no answer here") == (None, None)


def test_candidate_letters_flags_conflicts():
    assert candidate_letters("Answer: B") == {"B"}
    assert candidate_letters("\\boxed{A}\n\nAnswer: C") == {"A", "C"}
    # quoting the hint is not a second answer
    assert candidate_letters('The professor says "the answer is (A)".\n\nAnswer: C') == {"C"}
    assert candidate_letters(None) == set()


def test_split_think():
    assert split_think("<think>\nhmm\n</think>\n\nAnswer: B") == ("hmm", "Answer: B", True)
    assert split_think("hmm</think>Answer: A") == ("hmm", "Answer: A", True)
    assert split_think("<think>\nstill going") == ("still going", "", False)
