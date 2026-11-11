from cotaudit.data.review import VERDICT, bad_verdicts, read_reviewer_columns, review_sample, write_review


def rec(qid):
    t = {"question": f"q {qid}", "options": ["a", "b", "c", "d"]}
    return {"qid": qid, "subject": "s", "gold": "A", "text": {"en": t, "ml": t}}


def test_review_sample_is_balanced_and_stable():
    qs = {f"s/{i}": "stem" for i in range(50)} | {f"h/{i}": "humanities" for i in range(50)}
    a = review_sample(qs, ["stem", "humanities"], 10, seed=21)
    assert a == review_sample(qs, ["stem", "humanities"], 10, seed=21)
    assert sum(q.startswith("s/") for q in a) == 5


def test_rewrite_keeps_reviewer_columns(tmp_path):
    path = tmp_path / "review.csv"
    write_review(path, [rec("q1"), rec("q2")])
    text = path.read_text(encoding="utf-8-sig").replace("q2,s,A,q q2,a | b | c | d,q q2,a | b | c | d,,,",
                                                         "q2,s,A,q q2,a | b | c | d,q q2,a | b | c | d,bad,me,garbled")
    path.write_text(text, encoding="utf-8-sig")
    write_review(path, [rec("q1"), rec("q2")])
    cols = read_reviewer_columns(path)
    assert cols["q2"] == {VERDICT: "bad", "reviewer": "me", "notes": "garbled"}
    assert cols["q1"][VERDICT] == ""
    assert bad_verdicts(path) == {"q2"}
