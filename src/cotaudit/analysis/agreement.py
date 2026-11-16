"""Cohen's kappa between labellers, and between labellers and the judge (target >= 0.70)."""

from __future__ import annotations

from collections import Counter

import numpy as np


def cohen_kappa(a: list, b: list) -> float:
    """Unweighted Cohen's kappa for two equal-length label lists."""
    if len(a) != len(b) or not a:
        raise ValueError("need two non-empty label lists of the same length")
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in ca.keys() | cb.keys()) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def bootstrap_kappa(a: list, b: list, seed: int, n_boot: int = 2000) -> tuple[float, float, int]:
    """95% percentile bootstrap interval for kappa, resampling traces (pairs) with replacement.

    Returns (low, high, dropped). A resample where both raters use one and the same class has no
    defined kappa (expected agreement is 1), so it is dropped and counted in `dropped`, not
    scored as 1. If every resample is dropped the interval is (nan, nan).
    """
    a, b = np.asarray(a).astype(int), np.asarray(b).astype(int)
    idx = np.random.default_rng(seed).integers(0, len(a), size=(n_boot, len(a)))
    ra, rb = a[idx], b[idx]
    observed = (ra == rb).mean(axis=1)
    expected = sum((ra == k).mean(axis=1) * (rb == k).mean(axis=1) for k in np.union1d(a, b))
    defined = expected < 1 - 1e-12
    kappas = (observed[defined] - expected[defined]) / (1 - expected[defined])
    if not kappas.size:
        return (float("nan"), float("nan"), n_boot)
    low, high = np.percentile(kappas, [2.5, 97.5])
    return (float(low), float(high), int(n_boot - kappas.size))


def prevalence(labels: list) -> str:
    """Share of each class, e.g. "0:0.50 1:0.20 2:0.30". Kappa drops when one class is rare."""
    counts = Counter(int(x) for x in labels)
    return " ".join(f"{k}:{counts[k] / len(labels):.2f}" for k in sorted(counts))


def agreement_stats(a: list, b: list, seed: int, n_boot: int = 2000) -> dict:
    """n, percent agreement, class prevalence per rater, kappa and its bootstrap interval (D6)."""
    low, high, dropped = bootstrap_kappa(a, b, seed, n_boot)
    return {"n": len(a), "pct_agree": round(100 * sum(x == y for x, y in zip(a, b)) / len(a), 1),
            "prev_a": prevalence(a), "prev_b": prevalence(b), "kappa": round(cohen_kappa(a, b), 3),
            "ci_low": round(low, 3), "ci_high": round(high, 3), "boot_dropped": dropped}
