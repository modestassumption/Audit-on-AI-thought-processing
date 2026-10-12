"""Select the 300 questions and match them across en/hi/zh/ml.

Outputs (all deterministic for a given seed and exclusion list):
    data/questions.jsonl          selected questions, every language, gold + hinted letter
    data/reserve.jsonl            remaining eligible questions, in replacement order
    data/manifest.json            seed, counts, dataset revisions, output hashes
    data/review/ml_review_60.csv  Malayalam sample for native-speaker review

To drop a badly translated question, add its qid to configs/excluded_questions.txt
and rerun; it is replaced by the next reserve question from the same stratum.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter

from huggingface_hub import HfApi

from cotaudit.config import CONFIGS, DATA, load_experiment
from cotaudit.data import load
from cotaudit.data.match import match_sarvam_to_mmlu
from cotaudit.data.select import eligible_pool, hinted_letter, stratified_sample, stratum_of

EXCLUDED = CONFIGS / "excluded_questions.txt"


def read_excluded() -> set[str]:
    if not EXCLUDED.exists():
        return set()
    lines = EXCLUDED.read_text(encoding="utf-8").splitlines()
    return {ln.split("#")[0].strip() for ln in lines} - {""}


def dataset_revision(repo: str) -> str | None:
    try:
        return HfApi().dataset_info(repo).sha
    except Exception:
        return None


def write_jsonl(path, rows) -> str:
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    cfg = load_experiment()
    seed, dcfg = cfg["seed"], cfg["dataset"]
    strata = dcfg["strata"]
    rev = dcfg["revisions"]

    print("Loading datasets ...")
    mmlu = {r["sample_id"]: r for r in load.load_mmlu(rev[load.MMLU_REPO])}
    gm = {
        lang: {r["sample_id"]: r for r in load.load_global_mmlu(lang, rev[load.GLOBAL_MMLU_REPO])}
        for lang in ("en", "hi", "zh")
    }
    sarvam = {lang: load.load_sarvam(lang, rev[load.SARVAM_REPO]) for lang in ("en", "ml")}
    ml = match_sarvam_to_mmlu(list(mmlu.values()), sarvam["en"], sarvam["ml"])
    print(f"Malayalam rows matched to MMLU: {len(ml)}/{len(mmlu)}")

    pool = eligible_pool(gm, mmlu, ml, dcfg["cultural_sensitivity_label"])
    category = {sid: gm["en"][sid]["subject_category"] for sid in pool}
    pool = [sid for sid in pool if any(category[sid] in c for c in strata.values())]
    print(f"Eligible pool: {len(pool)} {dict(Counter(stratum_of(category[s], strata) for s in pool))}")

    selected, reserve = stratified_sample(pool, category, strata, dcfg["n_questions"], seed)

    excluded = read_excluded()
    replacements = {}
    for sid in [s for s in selected if s in excluded]:
        stratum = stratum_of(category[sid], strata)
        sub = next(
            r for r in reserve
            if r not in excluded and r not in selected and stratum_of(category[r], strata) == stratum
        )
        selected[selected.index(sid)] = sub
        replacements[sid] = sub
    reserve = [r for r in reserve if r not in selected and r not in excluded]
    if replacements:
        print(f"Replaced {len(replacements)} excluded questions")

    def record(sid: str) -> dict:
        gold = mmlu[sid]["answer"]
        texts = {lang: gm[lang][sid] for lang in ("hi", "zh")}
        texts["en"] = mmlu[sid]
        texts["ml"] = ml[sid]
        return {
            "qid": sid,
            "subject": mmlu[sid]["subject"],
            "subject_category": category[sid],
            "stratum": stratum_of(category[sid], strata),
            "gold": gold,
            "hinted": hinted_letter(sid, gold, seed),
            "sarvam_row": ml[sid]["row"],
            "text": {
                lang: {"question": texts[lang]["question"], "options": texts[lang]["options"]}
                for lang in cfg["languages"]
            },
        }

    questions = [record(s) for s in sorted(selected)]
    DATA.mkdir(exist_ok=True)
    q_hash = write_jsonl(DATA / "questions.jsonl", questions)
    r_hash = write_jsonl(DATA / "reserve.jsonl", [record(s) for s in reserve])

    # Malayalam review sample: equal share from each stratum.
    rng = random.Random(f"{seed}:ml_review")
    per = dcfg["ml_review_sample"] // len(strata)
    review = []
    for name in strata:
        ids = sorted(q["qid"] for q in questions if q["stratum"] == name)
        review += sorted(rng.sample(ids, per))
    by_id = {q["qid"]: q for q in questions}
    (DATA / "review").mkdir(exist_ok=True)
    with open(DATA / "review" / "ml_review_60.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["qid", "subject", "gold", "en_question", "en_options", "ml_question", "ml_options", "verdict(ok/bad)", "notes"])
        for sid in review:
            q = by_id[sid]
            w.writerow([
                sid, q["subject"], q["gold"],
                q["text"]["en"]["question"], " | ".join(q["text"]["en"]["options"]),
                q["text"]["ml"]["question"], " | ".join(q["text"]["ml"]["options"]),
                "", "",
            ])

    manifest = {
        "seed": seed,
        "n_questions": len(questions),
        "strata": dict(Counter(q["stratum"] for q in questions)),
        "subject_categories": dict(Counter(q["subject_category"] for q in questions)),
        "hinted_letters": dict(sorted(Counter(q["hinted"] for q in questions).items())),
        "eligible_pool": len(pool),
        "ml_matched": len(ml),
        "excluded": sorted(excluded),
        "replacements": replacements,
        "sources": rev,
        "latest_upstream": {repo: dataset_revision(repo) for repo in rev},
        "sha256": {"questions.jsonl": q_hash, "reserve.jsonl": r_hash},
    }
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("n_questions", "strata", "subject_categories", "hinted_letters")}, indent=2))


if __name__ == "__main__":
    main()
