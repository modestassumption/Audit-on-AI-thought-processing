"""Week 6 tests and intervals (proposal 4.7; owner: sub-team D).

- `hint_effect`: do the hints really change answers? Exact McNemar test per model x language x
  hint, pairing each hinted run with the same question's no-hint run, Holm-adjusted over cells.
- `influence_intervals`: a rate pooled over languages or hints counts the same question several
  times, so next to the Wilson interval (runs independent) it gives a bootstrap interval that
  resamples whole questions.
- `cell_rates`: rate per model x language x hint with a Wilson interval and, as the check the
  proposal asks for, an empirical-Bayes Beta-Binomial estimate (one Beta prior per model,
  fitted across its cells).
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


def rate_intervals(df: pd.DataFrame, outcome: str, by: list[str], n_boot: int = 2000,
                   seed: int = 21) -> pd.DataFrame:
    """Rate of the 0/1 column `outcome` per group, with a 95% Wilson interval (rows independent)
    and a 95% bootstrap interval that resamples whole questions (`qid`)."""
    rows = []
    for key, g in df.groupby(by):
        per_q = g.groupby("qid")[outcome].agg(["sum", "count"])
        k, n = int(per_q["sum"].sum()), int(per_q["count"].sum())
        lo, hi = wilson(k, n)
        blo, bhi = cluster_bootstrap(per_q["sum"], per_q["count"], n_boot, seed)
        rows.append({**dict(zip(by, key if isinstance(key, tuple) else (key,))),
                     "questions": len(per_q), "n": n, "k": k, "rate": k / n,
                     "wilson low": lo, "wilson high": hi, "bootstrap low": blo, "bootstrap high": bhi})
    return pd.DataFrame(rows)


def influence_intervals(hinted: pd.DataFrame, by: list[str], n_boot: int = 2000,
                        seed: int = 21) -> pd.DataFrame:
    """Influence rate per group (determined runs only) with a 95% Wilson interval and a 95%
    bootstrap interval over questions."""
    det = hinted[~hinted["undetermined"]]
    det = det.assign(influenced=det["influenced"].astype(int))
    return rate_intervals(det, "influenced", by, n_boot, seed).rename(
        columns={"n": "determined", "k": "influenced"})


# --- Beta-Binomial check on the per-cell rates (proposal 4.7, first bullet) -----------------

def betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta function I_x(a, b) (continued fraction, Lentz's method)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x > (a + 1) / (a + b + 2):  # the continued fraction converges fast below this point
        return 1.0 - betainc(b, a, 1.0 - x)
    front = math.exp(a * math.log(x) + b * math.log1p(-x)
                     - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))) / a
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 10_000):
        for num in (m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m)),
                    -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))):
            d = 1.0 + num * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + num / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return front * h


def beta_ppf(q: float, a: float, b: float) -> float:
    """Quantile of the Beta(a, b) distribution, by bisection on betainc."""
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if betainc(a, b, mid) < q else (lo, mid)
    return (lo + hi) / 2


def _betabinom_loglik(k: np.ndarray, n: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Beta-Binomial log-likelihood summed over cells (binomial coefficients dropped), for each
    (a, b) pair in the arrays a, b."""
    lg = np.vectorize(math.lgamma)
    out = -len(k) * (lg(a) + lg(b) - lg(a + b))
    for ki, ni in zip(k, n):
        out = out + lg(a + ki) + lg(b + ni - ki) - lg(a + b + ni)
    return out


def fit_beta_binomial(k, n) -> tuple[float, float]:
    """Maximum-likelihood Beta(a, b) prior for cell rates, from successes k and trials n per cell.

    Searched on mean a/(a+b) in (0, 1) and strength a+b in [0.1, 10,000] (a coarse grid, then a
    finer one around the best point). A strength at the upper end means the cells look like one
    shared rate. NaN with fewer than two cells that have trials.
    """
    k, n = np.asarray(k, dtype=float), np.asarray(n, dtype=float)
    k, n = k[n > 0], n[n > 0]
    if len(n) < 2:
        return (math.nan, math.nan)
    logit_mu = np.linspace(-7, 7, 57)
    log_s = np.linspace(math.log(0.1), math.log(1e4), 57)
    for _ in range(3):
        M, S = np.meshgrid(logit_mu, log_s)
        mu, s = 1 / (1 + np.exp(-M)), np.exp(S)
        ll = _betabinom_loglik(k, n, mu * s, (1 - mu) * s)
        i, j = np.unravel_index(np.argmax(ll), ll.shape)
        dm, ds = logit_mu[1] - logit_mu[0], log_s[1] - log_s[0]
        logit_mu = np.linspace(M[i, j] - 2 * dm, M[i, j] + 2 * dm, 21)
        log_s = np.clip(np.linspace(S[i, j] - 2 * ds, S[i, j] + 2 * ds, 21), math.log(0.1), math.log(1e4))
    m, s = 1 / (1 + math.exp(-M[i, j])), math.exp(S[i, j])
    return (m * s, (1 - m) * s)


def beta_binomial_estimates(k, n, level: float = 0.95) -> pd.DataFrame:
    """Empirical-Bayes rates: fit one Beta prior across the cells, then each cell's posterior
    Beta(a + k, b + n - k) gives a shrunken rate (posterior mean) and an equal-tailed interval.
    Small or extreme cells move towards the shared mean; large cells barely move."""
    a, b = fit_beta_binomial(k, n)
    tail = (1 - level) / 2
    rows = []
    for ki, ni in zip(k, n):
        if math.isnan(a) or ni == 0:
            rows.append({"bb rate": math.nan, "bb low": math.nan, "bb high": math.nan})
            continue
        pa, pb = a + ki, b + ni - ki
        rows.append({"bb rate": pa / (pa + pb), "bb low": beta_ppf(tail, pa, pb),
                     "bb high": beta_ppf(1 - tail, pa, pb)})
    return pd.DataFrame(rows, columns=["bb rate", "bb low", "bb high"])


def cell_rates(df: pd.DataFrame, outcome: str, by: list[str], pool_within: str = "model") -> pd.DataFrame:
    """Rate of the 0/1 column `outcome` per group: count, Wilson interval, and the
    Beta-Binomial estimate with the prior fitted across the groups of each `pool_within` value
    (default: one prior per model, shared by its language x hint cells)."""
    t = df.groupby(by)[outcome].agg(n="count", k="sum").reset_index()
    t["k"] = t["k"].astype(int)
    t["rate"] = t["k"] / t["n"]
    t[["wilson low", "wilson high"]] = [wilson(k, n) for k, n in zip(t["k"], t["n"])]
    parts = []
    for _, g in t.groupby(pool_within, sort=False):
        bb = beta_binomial_estimates(g["k"].to_numpy(), g["n"].to_numpy())
        parts.append(pd.concat([g.reset_index(drop=True), bb], axis=1))
    return pd.concat(parts, ignore_index=True) if parts else t
