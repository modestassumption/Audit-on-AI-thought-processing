"""Week 6 tests and intervals (proposal 4.7; owner: sub-team D).

- `hint_effect`: do the hints really change answers? Exact McNemar test per model x language x
  hint, pairing each hinted run with the same question's no-hint run, Holm-adjusted over cells.
- `influence_intervals`: a rate pooled over languages or hints counts the same question several
  times, so next to the Wilson interval (runs independent) it gives a bootstrap interval that
  resamples whole questions.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from cotaudit.analysis.influence import wilson

CELL = ["model", "lang", "condition"]


def mcnemar(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value from the two discordant counts.

    b: pairs where only the hinted run picked the hinted option; c: pairs where only the no-hint
    run did. With no effect, min(b, c) follows Binomial(b + c, 1/2).
    """
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1))
    return min(1.0, 2 * tail / 2 ** n)


def holm(pvalues) -> list[float]:
    """Holm step-down adjusted p-values, in the input order. NaN entries stay NaN."""
    p = [float(x) for x in pvalues]
    family = sorted((i for i, x in enumerate(p) if not math.isnan(x)), key=p.__getitem__)
    m, running, out = len(family), 0.0, [math.nan] * len(p)
    for rank, i in enumerate(family):
        running = max(running, min(1.0, (m - rank) * p[i]))
        out[i] = running
    return out


def hint_effect(hinted: pd.DataFrame, baseline_rep: int = 1) -> pd.DataFrame:
    """McNemar test per model x language x hint on picking the hinted option, with the hint vs.
    in the same question's no-hint run `baseline_rep`. Only pairs where both answers were
    extracted count. p-values are Holm-adjusted over all cells."""
    base = f"base{baseline_rep}"
    pairs = hinted[hinted["answer"].notna() & hinted[base].notna()]
    pairs = pairs.assign(with_hint=pairs["answer"] == pairs["hinted"],
                         without_hint=pairs[base] == pairs["hinted"])
    rows = []
    for (model, lang, hint), g in pairs.groupby(CELL):
        b = int((g["with_hint"] & ~g["without_hint"]).sum())
        c = int((g["without_hint"] & ~g["with_hint"]).sum())
        rows.append({"model": model, "lang": lang, "hint": hint, "pairs": len(g),
                     "picked with hint": int(g["with_hint"].sum()),
                     "picked without hint": int(g["without_hint"].sum()),
                     "only with hint": b, "only without hint": c, "p": mcnemar(b, c)})
    out = pd.DataFrame(rows, columns=["model", "lang", "hint", "pairs", "picked with hint",
                                      "picked without hint", "only with hint", "only without hint", "p"])
    out["p (Holm)"] = holm(out["p"])
    return out


def cluster_bootstrap(k, n, n_boot: int = 2000, seed: int = 21,
                      level: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap interval for sum(k) / sum(n), resampling whole clusters.

    k[i] and n[i] are the successes and trials of cluster i (here: the influenced and the
    determined hinted runs of one question within the group). NaN with fewer than two clusters,
    whose spread cannot be estimated.
    """
    k, n = np.asarray(k, dtype=float), np.asarray(n, dtype=float)
    if len(n) < 2 or n.sum() == 0:
        return (math.nan, math.nan)
    idx = np.random.default_rng(seed).integers(0, len(n), size=(n_boot, len(n)))
    trials = n[idx].sum(axis=1)
    rates = np.divide(k[idx].sum(axis=1), trials, out=np.full(n_boot, np.nan), where=trials > 0)
    tail = (1 - level) / 2
    lo, hi = np.nanquantile(rates, [tail, 1 - tail])
    return (float(lo), float(hi))


def influence_intervals(hinted: pd.DataFrame, by: list[str], n_boot: int = 2000,
                        seed: int = 21) -> pd.DataFrame:
    """Influence rate per group (determined runs only) with a 95% Wilson interval and a 95%
    bootstrap interval over questions."""
    det = hinted[~hinted["undetermined"]]
    rows = []
    for key, g in det.groupby(by):
        per_q = g.groupby("qid")["influenced"].agg(["sum", "count"])
        k, n = int(per_q["sum"].sum()), int(per_q["count"].sum())
        lo, hi = wilson(k, n)
        blo, bhi = cluster_bootstrap(per_q["sum"], per_q["count"], n_boot, seed)
        rows.append({**dict(zip(by, key if isinstance(key, tuple) else (key,))),
                     "questions": len(per_q), "determined": n, "influenced": k, "rate": k / n,
                     "wilson low": lo, "wilson high": hi, "bootstrap low": blo, "bootstrap high": bhi})
    return pd.DataFrame(rows)
