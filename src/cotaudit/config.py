from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = ROOT / "configs"
DATA = ROOT / "data"
RUNS = ROOT / "runs"


def load_experiment(path: Path = CONFIGS / "experiment.yaml") -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_hints(path: Path = CONFIGS / "hints.yaml") -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def unreviewed_entries(hints: dict, langs: list[str] | None = None) -> list[str]:
    """Paths of every translated entry still marked `reviewed: false`."""
    out = []
    for section in ("instructions", "hints"):
        for name, by_lang in hints[section].items():
            for lang, entry in by_lang.items():
                if (langs is None or lang in langs) and not entry.get("reviewed", False):
                    out.append(f"{section}.{name}.{lang}")
    for lang, entry in hints["subjects"].items():
        if (langs is None or lang in langs) and not entry.get("reviewed", False):
            out.append(f"subjects.{lang}")
    return out
