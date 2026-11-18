# Results summary (status 2026-11-18, 23:00 IST)

Every table in `results/` is regenerated from the runs and judge labels on `main` with
`bash scripts/regenerate_results.sh`. Runs are final (Groq runs frozen at 19:30 IST). Judge labels
are complete: every influenced trace that can be judged has a gpt-oss-120b label.

## Coverage

| | gpt-oss-20b | qwen3.8-27b | R1-Distill-Llama-8B |
|---|---|---|---|
| Current runs (of 6,900) | 6,900 | 5,936 | 6,900 |
| Questions with all 23 conditions (of 300) | 300 | 258 | 300 |
| Influenced traces that can be judged | 696 | 787 | 909 |

- **Missing runs:** qwen3.8-27b shard 6/7 (964 runs, 42 questions) was not finished before the
  freeze. Every other model × shard is complete (`docs/compute.md`).
- **Judging:** all 2,392 influenced traces that can be judged have a gpt-oss-120b label
  (696 gpt-oss-20b, 787 qwen3.8-27b and 909 R1-Distill; 347 of them, the last 320 R1-Distill
  traces and 27 shard 4/7 traces of gpt-oss-20b and qwen3.8-27b, judged by the same model on
  DeepInfra after the Groq keys hit their daily cap; one more R1-Distill influenced trace hit the
  token limit, so `runs.md` counts 910).
- **Stale runs:** 662 logged runs are left out everywhere because their question or prompt was
  replaced after the Malayalam review (`load_runs`).
- **Run health:** reasoning returned in 100% of runs, an answer extracted in 95.7%; 4.1% hit the
  token limit, almost all R1-Distill (13–19% of its English and Chinese runs).

## Influence: do hints change answers? (`runs.md`, `stats.md`, `rates.md`)

Share of determined hinted runs that switch to the hinted option, same-language hints:

| | Influenced | Rate | 95% CI (bootstrap over questions) |
|---|---|---|---|
| gpt-oss-20b | 624 / 3,562 | 17.5% | 15.6–19.5 |
| qwen3.8-27b | 745 / 3,048 | 24.4% | 21.9–27.2 |
| R1-Distill | 681 / 2,818 | 24.2% | 21.9–26.5 |
| Expert hint | 389 / 3,141 | 12.4% | |
| Leaked-key hint | 718 / 3,117 | 23.0% | |
| Metadata hint | 943 / 3,170 | 29.7% | |

- **Hints work:** answers move towards the hinted option in 43 of 45 model × language × hint
  cells (McNemar, Holm p < 0.05). Without a hint, the hinted option is picked in 7.5% of runs.
- **Range:** from 3.1% (qwen3.8-27b, English, expert) to 63.0% (qwen3.8-27b, Malayalam,
  metadata). The metadata hint is the strongest overall and the expert hint the weakest.
- **Subject area:** influence is higher for humanities (26.7%) than STEM (16.4%) questions.
- **Baseline accuracy:** gpt-oss-20b 78–89% and qwen3.8-27b 84–91% across the four languages;
  R1-Distill drops from 72% (en) to 38% (ml).

## Faithfulness: is the hint admitted? (`rates.md`, `rates_loose.md`, `regression.md`)

Level 2 means the reasoning presents the hint as a reason for its answer
(`docs/scoring_guide.md`). Same-language hints:

| | Level 2 | 95% CI | Level 1 or 2 (loose) |
|---|---|---|---|
| gpt-oss-20b | 479 / 610 = 78.5% | 74.6–82.1 | 91.1% |
| qwen3.8-27b | 700 / 737 = 95.0% | 93.3–96.5 | 98.5% |
| R1-Distill | 258 / 674 = 38.3% | 33.9–42.6 | 56.4% |

- **H1, model (GEE, 2,021 traces, 270 questions):** qwen3.8-27b admits the hint far more often
  than gpt-oss-20b (OR 5.62, 95% CI 3.80–8.30) and R1-Distill far less (OR 0.17, 0.13–0.23); both
  Holm p < 0.001.
- **H2, language:** only Malayalam differs significantly from English after Holm: Malayalam OR 0.60
  (0.40–0.91), Holm p = 0.045; Hindi 1.54 (1.01–2.34), Holm p = 0.086; Chinese 0.75 (0.50–1.15),
  Holm p = 0.188.
- **H3, hint type:** no difference (expert vs. leaked OR 0.93, metadata vs. leaked 1.09, both Holm p = 1.0).
- **Subject area:** humanities traces admit the hint more often than STEM (OR 1.43, 1.06–1.94,
  Holm p = 0.021).
- **Model × language interaction:** not significant (χ² = 12.43, 6 df, p = 0.053).
- **Restate-only as Level 2** (`regression_restate.md`): four of the five comparisons stay
  significant (the three model pairs and subject area); Malayalam vs. English does not (Holm
  p = 0.175), and no other becomes significant.

## H4: English hint inside a non-English question (`h4.md`)

- **Influence:** the English and own-language expert hints differ in 1 of 9 model × language
  cells: R1-Distill in Malayalam, where the English hint moves more answers (127 vs. 86,
  Holm p < 0.001).
- **Admission:** differs in 2 of 9 cells, both in Malayalam: R1-Distill again (73.8% vs. 31.8%
  admitted, Holm p < 0.001) and gpt-oss-20b (92.0% vs. 47.4%, Holm p = 0.008).

## Reasoning language (`language_subject.md`, `figures/reasoning_language.svg`)

- **The Groq models reason in English** on almost every non-English question: gpt-oss-20b stays
  in the question's language in 1.6% of Hindi, Chinese and Malayalam traces, qwen3.8-27b in 6.0%
  (all Chinese). R1-Distill reasons in Chinese on every Chinese question and on 23% of Hindi ones.
- **Switching and admission:** traces that switch away from the question's language are not
  significantly different in faithfulness (GEE OR 1.31, 95% CI 0.78–2.18, p = 0.31). Few traces stay in the
  question's language, so this comparison is weak.

## Judge reliability

- **Second judge (qwen3.8-27b) on the 338-trace sample:** κ = 0.68 (95% CI 0.58–0.77; 88.8%
  agreement, n = 329) on Level 2 vs. not, and κ = 0.72 on the loose measure
  (`labels/human/main/agreement.csv`). This shows the two judges are consistent, not that they
  are correct.
- **Keyword-filter flags:** 126 F1 (judge Level 0 with a strong keyword hit), 43 F2 (judge Level 2
  with no hit) and 37 Q (quote not found in the trace) among the current labels. The review list
  is `labels/gpt-oss-120b/review_sample.csv`.
- **Flag review:** on the first 11 flagged traces (`labels/gpt-oss-120b/flag_review.csv`), 9 of
  the 10 F1 cases quote the hint and use it, so the judge's rare Level 0 labels are mostly wrong.
  Reviewed by Visakh Vivek. The main tables use the judge's levels; the review is reported as a
  check on the judge.
- **No human labels** were collected, so the human-labels-only check was not run.

## Limitations

- qwen3.8-27b is missing shard 6/7 (42 of 300 questions).
- Faithfulness rests on one LLM judge, checked against a second judge and the keyword filter,
  not against human labels.
- The Chinese and Malayalam keyword lists were not reviewed by a native speaker.
