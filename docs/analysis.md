# Analysis: sample size, tests, intervals, figures

**Owner:** Sashwath Swaminathan (2024A3PS0361H), sub-team D. Proposal §4.7 and §5.

| Week | Work | Code | Status |
|---|---|---|---|
| 5 (Nov 2–8) | Sample-size table; pilot rule (below 15% influence → 450 questions) | `src/cotaudit/analysis/power.py`, `scripts/sample_size.py` | Done. The 300 vs. 450 decision waits for the pilot runs. |
| 6 (Nov 9–15) | McNemar tests (hint vs. no hint), Holm-adjusted; bootstrap intervals over questions | `src/cotaudit/analysis/stats.py`, `scripts/report_stats.py` | Code done and tested. Numbers once the main runs are pushed. |
| 6 (Nov 9–15) | Logistic regression with GEE for H1–H3; model × language interaction test | `src/cotaudit/analysis/regression.py`, `scripts/regression.py` | Code done and tested on simulated labels. Numbers once the judge labels (sub-team C) are pushed. |
| 6 (Nov 9–15) | Rates per model × language × hint: Wilson intervals plus Beta-Binomial estimates as a check | `src/cotaudit/analysis/stats.py`, `scripts/rates.py` | Code done and tested on simulated runs and labels. Numbers once runs and labels are pushed. |
| 6 (Nov 9–15) | H4: McNemar on influence and two-proportion z-test on faithfulness (English vs. own-language expert hint) | `src/cotaudit/analysis/h4.py`, `scripts/h4.py` | Code done and tested on simulated runs and labels. Numbers once the H4 runs and labels are pushed. |
| 7 (Nov 16–22) | Reasoning-language analysis (which language each trace reasons in; is the hint admitted less often when the reasoning switches away from the question's language?) and subject-area rates | `src/cotaudit/analysis/language.py`, `scripts/language_subject.py` | Code done and tested on simulated runs and labels. On the October smoke runs, qwen3.8-27b reasoned in English on all 5 Malayalam questions. Numbers once runs and labels are pushed. |
| 7 (Nov 16–22) | Figures: influence and faithfulness per model × language × hint, H4 (English vs. own-language hint), language of the reasoning, H1–H3 odds ratios | `src/cotaudit/analysis/figures.py`, `scripts/figures.py` | Code done and tested; drawn on simulated runs and labels and on the smoke runs. Written as SVG, so no plotting library is added. Figures with real numbers once runs and labels are pushed. |

## Run

```bash
uv run python scripts/sample_size.py
uv run python scripts/report_stats.py --out results/stats.md
uv run python scripts/regression.py --out results/regression.md
uv run python scripts/regression.py --restate-as-admitted          # sensitivity check (sub-team C, D3b)
uv run python scripts/rates.py --out results/rates.md
uv run python scripts/h4.py --out results/h4.md
uv run python scripts/language_subject.py --out results/language_subject.md
uv run python scripts/figures.py                                   # SVG files in results/figures/
uv run pytest tests/test_power.py tests/test_stats.py tests/test_regression.py tests/test_h4.py tests/test_language.py tests/test_figures.py
```

## Choices

- McNemar pairs each hinted run with the same question's first no-hint run (`--baseline-rep 2`
  uses the second), so each question counts once per model × language × hint.
- Rates pooled over languages or hints count each question several times, so their bootstrap
  intervals resample whole questions: 2,000 resamples, percentile interval, seed 21
  (`configs/experiment.yaml`).
- Regression: influenced traces with a usable judge level, same-language hints only (H4 is tested
  separately). GEE with an independence working correlation, grouped by question, robust
  (sandwich) errors with a G/(G−1) correction. Reference levels: English, the leaked-key hint,
  STEM and the first model alphabetically. Holm is applied within each family (languages vs.
  English, model pairs, hint pairs). The interaction is tested jointly on a separate fit, so the
  main contrasts are averaged over models. Written with numpy only, so no new dependency.
- Beta-Binomial check: one Beta prior per model, fitted by maximum likelihood across that model's
  language × hint cells; each cell's posterior mean and 95% equal-tailed interval are reported
  next to the Wilson interval. Small cells are pulled towards the model's typical rate, so a big
  gap between the two columns flags a cell resting on few runs.
- H4 compares the expert hint in English with the expert hint in the question's own language
  (the H4 runs use the expert hint only), per model and question language. Influence: McNemar,
  paired by question. Faithfulness: two-proportion z-test as in the proposal, although the same
  question can appear in both groups, so its p-values are slightly optimistic. Holm over the nine
  model × language cells of each test.
- Reasoning language is read from the script of the reasoning: the language whose script holds at
  least 60% of the words (`--threshold`), otherwise "mixed". One-letter Latin tokens (option
  letters, variables) are ignored and each Chinese character counts as one word. The
  switching comparison uses same-language hints in Hindi, Chinese and Malayalam questions: a
  two-proportion z-test per model × language (Holm) and one GEE odds ratio adjusted for model,
  language, hint type and subject area. The model chooses its reasoning language, so this is an
  association, not a causal effect.
- Subject areas are STEM, Social Sciences and Humanities from `data/questions.jsonl`
  (`--area stratum` gives the regression's STEM vs. humanities split). Each question appears in
  several languages and hints, so the intervals resample whole questions.
- Figures are SVG written directly by `cotaudit.analysis.figures`, since the project has no
  plotting library. Rates show the dot and its 95% bootstrap interval over questions, one row per
  model × language and one colour per hint type (the same colour for a hint in every figure);
  odds ratios use a log axis with a dashed line at 1. Hovering over a mark in a browser shows the
  exact numbers. The colours come from a colour-blind-checked order, and labels are in grey text,
  not in the series colours.
