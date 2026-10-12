"""The experimental grid (proposal 4.5): 23 prompts per question, 6,900 for 300 questions."""

from __future__ import annotations

import hashlib

from cotaudit.prompts import render_prompt

BASELINE = "none"


def condition_specs(cfg: dict) -> list[dict]:
    """(lang, hint_type, hint_lang, rep) tuples for one question."""
    specs = []
    for lang in cfg["languages"]:
        for rep in range(1, cfg["baseline_repeats"] + 1):
            specs.append({"lang": lang, "hint_type": BASELINE, "hint_lang": None, "rep": rep})
        for hint_type in cfg["hint_types"]:
            specs.append({"lang": lang, "hint_type": hint_type, "hint_lang": lang, "rep": 1})
    cross = cfg["cross_lingual"]
    for lang in cfg["languages"]:
        if lang != cross["hint_lang"]:
            specs.append({"lang": lang, "hint_type": cross["hint_type"], "hint_lang": cross["hint_lang"], "rep": 1})
    return specs


def condition_id(qid: str, spec: dict) -> str:
    return f"{qid}|{spec['lang']}|{spec['hint_type']}|{spec['hint_lang'] or '-'}|{spec['rep']}"


def build_conditions(questions: list[dict], cfg: dict, hints: dict) -> list[dict]:
    rows = []
    for q in questions:
        for spec in condition_specs(cfg):
            hinted = spec["hint_type"] != BASELINE
            prompt = render_prompt(
                hints, q, spec["lang"],
                spec["hint_type"] if hinted else None,
                spec["hint_lang"],
            )
            rows.append({
                "condition_id": condition_id(q["qid"], spec),
                "qid": q["qid"],
                "subject": q["subject"],
                "stratum": q["stratum"],
                "gold": q["gold"],
                "hinted": q["hinted"],
                **spec,
                "prompt": prompt,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            })
    return rows
