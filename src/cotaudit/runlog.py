"""Append-only JSONL run logs under runs/<model>/<YYYY-MM-DD>-<tag>.jsonl.

The tag (default: the computer's name) keeps logs written by different team members in
separate files, so pushing them never conflicts.

A run is done once a record with its run_id exists in any file in the model's directory,
so interrupted jobs resume by skipping those ids. Failed calls go to errors-<tag>.jsonl and are retried
on the next invocation.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

from cotaudit.config import RUNS


def run_id(model: str, condition_id: str) -> str:
    return hashlib.sha256(f"{model}|{condition_id}".encode("utf-8")).hexdigest()[:16]


def default_tag() -> str:
    return re.sub(r"[^a-z0-9]+", "-", platform.node().lower()).strip("-") or "local"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RunLog:
    def __init__(self, model: str, root: Path = RUNS, tag: str | None = None):
        self.dir = root / model
        self.tag = tag or default_tag()
        self.dir.mkdir(parents=True, exist_ok=True)

    def completed_ids(self) -> set[str]:
        done = set()
        for path in self.dir.glob("20*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    done.add(json.loads(line)["run_id"])
        return done

    def _append(self, path: Path, record: dict) -> None:
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def write(self, record: dict) -> None:
        self._append(self.dir / f"{record['timestamp_utc'][:10]}-{self.tag}.jsonl", record)

    def write_error(self, record: dict) -> None:
        self._append(self.dir / f"errors-{self.tag}.jsonl", record)
