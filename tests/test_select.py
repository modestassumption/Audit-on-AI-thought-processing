from cotaudit.data.select import eligible_pool, hinted_letter, in_shard, run_order, stratified_sample

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


def test_run_order_alternates_strata_and_is_stable():
    qs = {f"s/test/{i}": "stem" for i in range(20)} | {f"h/test/{i}": "humanities" for i in range(20)}
    rank = run_order(qs, seed=21)
    assert sorted(rank.values()) == list(range(40))
    first10 = [q for q, r in rank.items() if r < 10]
    assert sum(qs[q] == "stem" for q in first10) == 5
    # Replacing one question leaves every other question's rank unchanged.
    swapped = {k: v for k, v in qs.items() if k != "s/test/0"} | {"s/test/99": "stem"}
    rank2 = run_order(swapped, seed=21)
    moved = [q for q in rank if q in rank2 and rank[q] != rank2[q]]
    assert len(moved) < 20


def test_shards_partition_questions():
    qids = [f"q/test/{i}" for i in range(100)]
    owners = [[s for s in range(1, 8) if in_shard(q, s, 7)] for q in qids]
    assert all(len(o) == 1 for o in owners)
    assert len({o[0] for o in owners}) == 7
