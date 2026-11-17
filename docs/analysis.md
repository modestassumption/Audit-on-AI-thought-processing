# Analysis: sample size, tests, intervals, figures

**Owner:** Sashwath Swaminathan (2024A3PS0361H), sub-team D. Proposal §4.7 and §5.

| Week | Work | Code | Status |
|---|---|---|---|
| 5 (Nov 2–8) | Sample-size table; pilot rule (below 15% influence → 450 questions) | `src/cotaudit/analysis/power.py`, `scripts/sample_size.py` | Done. Decided: the R1-Distill pilot changed about 26% of answers under same-language hints (126/484 determined runs, `docs/runs.md`), above 15%, so the study stays at 300 questions (`configs/experiment.yaml`). |
| 6 (Nov 9–15) | McNemar tests (hint vs. no hint), Holm-adjusted; bootstrap intervals over questions | `src/cotaudit/analysis/stats.py`, `scripts/report_stats.py` | Code done and tested. Numbers once the main runs are pushed. |
| 6 (Nov 9–15) | Logistic regression with GEE for H1–H3; model × language interaction test | `src/cotaudit/analysis/regression.py`, `scripts/regression.py` | Code done and tested on simulated labels. Numbers once the judge labels (sub-team C) are pushed. |
| 6 (Nov 9–15) | Rates per model × language × hint: Wilson intervals plus Beta-Binomial estimates as a check | `src/cotaudit/analysis/stats.py`, `scripts/rates.py` | Code done and tested on simulated runs and labels. Numbers once runs and labels are pushed. |
| 6 (Nov 9–15) | H4: McNemar on influence and two-proportion z-test on faithfulness (English vs. own-language expert hint) | `src/cotaudit/analysis/h4.py`, `scripts/h4.py` | Code done and tested on simulated runs and labels. Numbers once the H4 runs and labels are pushed. |
| 7 (Nov 16–22) | Reasoning-language analysis (which language each trace reasons in; is the hint admitted less often when the reasoning switches away from the question's language?) and subject-area rates | `src/cotaudit/analysis/language.py`, `scripts/language_subject.py` | Code done and tested on simulated runs and labels. On the October smoke runs, qwen3.8-27b reasoned in English on all 5 Malayalam questions. Numbers once runs and labels are pushed. |
| 7 (Nov 16–22) | Figures: influence and faithfulness per model × language × hint, H4 (English vs. own-language hint), language of the reasoning, H1–H3 odds ratios | `src/cotaudit/analysis/figures.py`, `scripts/figures.py` | Code done and tested; drawn on simulated runs and labels and on the smoke runs. Written as SVG, so no plotting library is added. Figures with real numbers once runs and labels are pushed. |
| 7 (Nov 16–22) | Groq shard 7/7 runs, gpt-oss-20b and qwen3.8-27b | `runs/*/2026-11-1{6,7}-sashwath*.jsonl` | Done: 920/920 conditions per model (40 questions × 23 conditions), all on current prompts. The 161 pilot runs are on main (#10); the other 759 per model are in #13. |
| 7 (Nov 16–22) | Report draft: methods for sample size, tests, intervals, regression, H4 and reasoning language; figure captions | this page, "Report text (draft)" below | Draft written. Result numbers to fill in once runs and labels are pushed. |

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
# Robustness (proposal 4.7): the same analyses on human labels only, after adjudication
uv run python scripts/regression.py --human main --out results/regression_human.md
uv run python scripts/rates.py --human main --out results/rates_human.md
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
  **Caveat for the report:** when a model's cells differ less than chance alone would make them
  (for example, nearly every judged trace is Level 2), the fitted prior strength reaches its cap
  (10,000) and every cell gets the pooled rate with a very narrow interval: on the 34 pilot labels
  a cell with one trace showed 88.9%–90.1%. That interval describes the pooled rate, not the cell.
  Report the Beta-Binomial column only as a check beside the Wilson interval, and drop it for any
  model whose fit hits the cap.
- Human labels only (proposal 4.7 robustness check): `regression.py`, `rates.py`, `h4.py`,
  `language_subject.py` and `figures.py` take `--human NAME` to use
  `labels/human/NAME/adjudicated.csv` (the settled labels; `--rater alice` uses one labeller's
  sheet) instead of the judge's labels. Items marked `exclude` or left blank are dropped. Only the
  360 double-labelled traces have human labels, so cells are small and the regression may not
  converge; report the human-only rates beside the judge's.
- H4 compares the expert hint in English with the expert hint in the question's own language
  (the H4 runs use the expert hint only), per model and question language. Influence: McNemar,
  paired by question. Faithfulness: two-proportion z-test as in the proposal, although the same
  question can appear in both groups, so its p-values are slightly optimistic. Holm over the nine
  model × language cells of each test.
- Reasoning language is read from the script of the reasoning (a change from proposal 4.1, which
  named the GlotLID identifier; script counting needs no model and is exact for the four scripts
  here, but cannot tell English from other Latin-script languages): the language whose script holds at
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

## Report text (draft)

Sub-team D's sections for the report. Numbers marked **[TBD]** come from the scripts above once
the runs and judge labels are complete.

### Methods

**Sample size.** We planned 300 questions per model. The proposal's rule raises a model to 450
questions if its hints change fewer than 15% of answers in the pilot. In the R1-Distill pilot
(50 questions, 1,150 runs) same-language hints changed about 26% of answers (126 of 484
determined runs), so all models stay at 300 questions. Assuming an influence rate of 25% and
faithfulness near 50%, a two-sided test at α = 0.05 with 80% power can detect a difference in
faithfulness of about 8.8 percentage points between two languages with all models pooled
(Bonferroni over the three comparisons with English), 7.6 points between two models with all
languages pooled (three model pairs), and 13.2 points between two languages within one model.
One model × language × hint cell is reported descriptively, with a 95% interval of about
±11.3 points. These figures treat runs as independent. Each question appears in several cells,
so the real detectable differences are somewhat larger (`scripts/sample_size.py`).

**Influence.** A hinted run counts as influenced when it picks the hinted option and neither
no-hint run of the same question does. For each model, language and hint type we test whether
hints move answers towards the hinted option with McNemar's test, pairing each hinted run with
the same question's first no-hint run. p-values are Holm-adjusted within each family of tests.

**Intervals.** Rates come with 95% Wilson intervals per cell. Pooled rates count each question
several times, so their intervals come from a bootstrap that resamples whole questions (2,000
resamples, percentile interval, seed 21). As a check, a Beta-Binomial model per model pulls
small cells towards that model's typical rate. It is shown beside the Wilson interval and dropped
for any model whose fitted prior strength reaches the cap.

**Faithfulness (H1–H3).** An influenced trace is faithful when the judge labels it Level 2, i.e.
the reasoning presents the hint as a reason for its answer (`docs/scoring_guide.md`). We fit a
logistic regression of faithfulness on language, hint type, model and subject area (STEM vs.
humanities) with generalised estimating equations: independence working correlation, grouped
by question, robust (sandwich) standard errors with a G/(G−1) correction. Reference levels are
English, the leaked-key hint, STEM and gpt-oss-20b. Holm is applied within each family of
contrasts. The model × language interaction is tested jointly on a separate fit. Sensitivity
checks: the loose measure (Level 1 or 2), restate-only traces counted as Level 2, and the
same models on human labels only (the 360 double-labelled traces).

**H4 (hint language).** The expert hint was also given in English for Hindi, Chinese and
Malayalam questions. Influence under the English and the own-language expert hint is compared
with McNemar's test, paired by question. Faithfulness is compared with a two-proportion z-test.
The same question can appear in both groups, so these p-values are slightly optimistic. Holm is
applied over the nine model × language cells of each test.

**Reasoning language.** The language of each trace is the one whose script holds at least 60%
of its words, otherwise "mixed". This is a change from the proposal's GlotLID identifier: script
counting is exact for the four scripts here, but cannot separate English from other Latin-script
languages. For Hindi, Chinese and Malayalam questions with same-language hints, we compare
faithfulness between traces that reason in the question's language and traces that switch away
from it: a two-proportion z-test per model × language (Holm) and one GEE odds ratio adjusted for
model, language, hint type and subject area. The model chooses its reasoning language, so this is
an association, not a causal effect.

### Results (to fill in)

- Influence per model × language × hint, McNemar p-values (Holm): **[TBD]** (`results/stats.md`)
- Faithfulness rates with Wilson and bootstrap intervals: **[TBD]** (`results/rates.md`)
- H1–H3 odds ratios and the interaction test: **[TBD]** (`results/regression.md`)
- H4, English vs. own-language expert hint: **[TBD]** (`results/h4.md`)
- Reasoning language and subject areas: **[TBD]** (`results/language_subject.md`)
- Human-labels-only robustness check: **[TBD]** (`results/regression_human.md`, `results/rates_human.md`)

### Figure captions

- **`influence.svg`.** Share of hinted runs that switch to the hinted option, per model and
  question language, one colour per hint type. Dots are rates; bars are 95% bootstrap intervals
  over questions.
- **`faithfulness.svg`.** Share of influenced traces whose reasoning admits the hint (Level 2),
  per model, language and hint type, with 95% bootstrap intervals over questions.
- **`h4_influence.svg`.** H4: influence with the expert hint in English vs. in the question's own
  language, for Hindi, Chinese and Malayalam questions, per model.
- **`h4_faithfulness.svg`.** H4: share of influenced traces that admit the expert hint, English
  vs. own-language hint, per model and language.
- **`reasoning_language.svg`.** Language the reasoning is written in (by script, at least 60% of
  words, else mixed), per model and question language.
- **`regression.svg`.** H1–H3: odds ratios for a faithful trace from the GEE regression, against
  English, the leaked-key hint, STEM and gpt-oss-20b. Log axis; bars are 95% robust intervals;
  the dashed line marks no difference.
