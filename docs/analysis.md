# Analysis: sample size, tests, intervals, figures

**Owner:** Sashwath Swaminathan (2024A3PS0361H), sub-team D. Proposal §4.7 and §5.

| Week | Work | Code | Status |
|---|---|---|---|
| 5 (Nov 2–8) | Sample-size table; pilot rule (below 15% influence → 450 questions) | `src/cotaudit/analysis/power.py`, `scripts/sample_size.py` | Done. The 300 vs. 450 decision waits for the pilot runs. |
| 6 (Nov 9–15) | McNemar tests (hint vs. no hint); bootstrap intervals over questions | | In progress |
| 6 (Nov 9–15) | Logistic regression with GEE for H1–H3 | | Waits for the judge labels (sub-team C) |
| 7 (Nov 16–22) | Reasoning-language and subject analysis; figures | | Planned |

## Run

```bash
uv run python scripts/sample_size.py
```
