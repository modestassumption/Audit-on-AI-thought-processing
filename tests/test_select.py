from cotaudit.data.select import eligible_pool, hinted_letter, stratified_sample

STRATA = {"stem": ["STEM"], "humanities": ["Humanities", "Social Sciences"]}


def test_stratified_sample_is_balanced_and_deterministic():
    cats = ["STEM", "Humanities", "Social Sciences"]
    category = {f"s/test/{i}": cats[i % 3] for i in range(30)}
    pool = sorted(category)
    a = stratified_sample(pool, category, STRATA, 10, seed=1)
    assert a == stratified_sample(pool, category, STRATA, 10, seed=1)
    selected, reserve = a
    assert sum(category[s] == "STEM" for s in selected) == 5
    assert not set(selected) & set(reserve)
    assert len(selected) + len(reserve) == len(pool)


def test_hinted_letter_is_wrong_and_stable():
    for i in range(200):
        gold = "ABCD"[i % 4]
        h = hinted_letter(f"q/{i}", gold, seed=21)
        assert h != gold and h in "ABCD"
        assert h == hinted_letter(f"q/{i}", gold, seed=21)


def test_eligible_pool_requires_ca_ml_and_agreeing_keys():
    def g(label, ans):
        return {"cultural_sensitivity_label": label, "answer": ans}

    gm = {
        lang: {"a": g("CA", "A"), "b": g("CS", "A"), "c": g("CA", "A"),
               "d": g("CA", "B" if lang == "zh" else "A")}
        for lang in ("en", "hi", "zh")
    }
    mmlu = {k: {"answer": "A"} for k in "abcd"}
    ml = {"a": {"answer": "A"}, "b": {"answer": "A"}, "d": {"answer": "A"}}
    assert eligible_pool(gm, mmlu, ml, "CA") == ["a"]
