"""Groq chat-completions runner with per-key rate-limit cooldowns.

Keys come from every GROQ_API_KEY* environment variable (one per team member). On a 429 the key
is rested for its retry-after period and the next key is used; if every key is resting for longer
than `max_wait_s`, QuotaExhausted is raised so the script can stop cleanly and resume later.
"""

from __future__ import annotations

import os
import time

import groq
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

TRANSIENT = (groq.APIConnectionError, groq.APITimeoutError, groq.InternalServerError)
PASSTHROUGH_PARAMS = ("reasoning_effort", "include_reasoning", "reasoning_format")


class QuotaExhausted(RuntimeError):
    pass


def keys_from_env() -> dict[str, str]:
    """{alias: key}; aliases (not keys) are what gets logged."""
    keys = {
        name.removeprefix("GROQ_API_KEY").strip("_").lower() or "default": value
        for name, value in sorted(os.environ.items())
        if name.startswith("GROQ_API_KEY") and value.strip()
    }
    if not keys:
        raise SystemExit("No GROQ_API_KEY* set. Copy .env.example to .env and add a key.")
    return keys


def _retry_after(err: groq.RateLimitError, default: float = 60.0) -> float:
    try:
        return float(err.response.headers.get("retry-after", default))
    except (TypeError, ValueError):
        return default


class GroqRunner:
    def __init__(self, model_cfg: dict, max_completion_tokens: int, keys: dict[str, str],
                 max_wait_s: float = 900.0):
        self.model_cfg = model_cfg
        self.clients = {alias: groq.Groq(api_key=k, max_retries=0, timeout=300) for alias, k in keys.items()}
        self.rest_until = {alias: 0.0 for alias in keys}
        self.max_wait_s = max_wait_s
        self.params = {
            "temperature": model_cfg["temperature"],
            "top_p": model_cfg["top_p"],
            "max_completion_tokens": max_completion_tokens,
            **{k: model_cfg[k] for k in PASSTHROUGH_PARAMS if k in model_cfg},
        }

    def _next_key(self) -> str:
        alias = min(self.rest_until, key=self.rest_until.get)
        wait = self.rest_until[alias] - time.time()
        if wait > self.max_wait_s:
            raise QuotaExhausted(f"All Groq keys rate-limited; earliest frees in {wait / 60:.0f} min")
        if wait > 0:
            print(f"  all keys resting, sleeping {wait:.0f}s")
            time.sleep(wait)
        return alias

    @retry(retry=retry_if_exception_type(TRANSIENT), stop=stop_after_attempt(4),
           wait=wait_exponential(multiplier=2, max=60), reraise=True)
    def _call(self, alias: str, prompt: str):
        return self.clients[alias].chat.completions.create(
            model=self.model_cfg["model_id"],
            messages=[{"role": "user", "content": prompt}],
            **self.params,
        )

    def generate(self, prompt: str) -> dict:
        while True:
            alias = self._next_key()
            start = time.time()
            try:
                resp = self._call(alias, prompt)
            except groq.RateLimitError as err:
                self.rest_until[alias] = time.time() + _retry_after(err)
                continue
            choice = resp.choices[0]
            return {
                "model_returned": resp.model,
                "system_fingerprint": getattr(resp, "system_fingerprint", None),
                "reasoning": getattr(choice.message, "reasoning", None),
                "content": choice.message.content,
                "finish_reason": choice.finish_reason,
                "usage": resp.usage.model_dump() if resp.usage else None,
                "latency_s": round(time.time() - start, 2),
                "key_alias": alias,
            }
