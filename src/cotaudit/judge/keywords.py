"""Keyword filter: flag reasoning that may mention the hint (configs/keywords.yaml)."""

from __future__ import annotations

import yaml

from cotaudit.config import CONFIGS


def load_keywords(path=CONFIGS / "keywords.yaml") -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def terms_for(keywords: dict, hint_type: str, langs: set[str]) -> list[str]:
    """Generic + hint-type terms for every language in `langs`, plus English (models often switch)."""
    langs = set(langs) | {"en"}
    out = []
    for section in ("any", hint_type):
        for lang in sorted(langs):
            out += keywords.get(section, {}).get(lang, {}).get("terms", [])
    return sorted(set(out))


def keyword_hits(reasoning: str | None, keywords: dict, hint_type: str, langs: set[str]) -> list[str]:
    text = (reasoning or "").casefold()
    return [t for t in terms_for(keywords, hint_type, langs) if t.casefold() in text]
