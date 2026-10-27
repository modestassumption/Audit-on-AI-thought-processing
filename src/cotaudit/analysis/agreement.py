"""Cohen's kappa between labellers, and between labellers and the judge (target >= 0.70)."""

from __future__ import annotations

from collections import Counter


def cohen_kappa(a: list, b: list) -> float:
    """Unweighted Cohen's kappa for two equal-length label lists."""
    if len(a) != len(b) or not a:
        raise ValueError("need two non-empty label lists of the same length")
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in ca.keys() | cb.keys()) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)
