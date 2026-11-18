# Results summary (status 2026-11-18, 20:30 IST)

Every table in `results/` is regenerated from the runs and judge labels on `main` with
`bash scripts/regenerate_results.sh`. Runs are final (Groq runs frozen at 19:30 IST). Judge labels
were still coming in when this page was written, so rerun the script after the last labels are
merged and update the faithfulness numbers below.

## Coverage

| | gpt-oss-20b | qwen3.8-27b | R1-Distill-Llama-8B |
|---|---|---|---|
| Current runs (of 6,900) | 6,900 | 5,936 | 6,900 |
| Questions with all 23 conditions (of 300) | 300 | 258 | 300 |
| Influenced traces | 696 | 787 | 909 |

- **Missing runs:** qwen3.8-27b shard 6/7 (964 runs, 42 questions) was not finished before the
  freeze. Every other model × shard is complete (`docs/compute.md`).
- **Judging:** 1,872 of the 2,392 influenced traces have a gpt-oss-120b label. Traces are judged
  in a seeded order stratified by model × language × condition, so a partial set is
  representative (D5).
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
| gpt-oss-20b | 415 / 532 = 78.0% | 73.9–81.9 | 91.0% |
| qwen3.8-27b | 606 / 635 = 95.4% | 93.7–97.0 | 98.4% |
| R1-Distill | 177 / 442 = 40.0% | 35.1–45.2 | 58.8% |

- **H1, model (GEE, 1,609 traces, 260 questions):** qwen3.8-27b admits the hint far more often
  than gpt-oss-20b (OR 6.40, 95% CI 4.21–9.74) and R1-Distill far less (OR 0.20, 0.14–0.27); both
  Holm p < 0.001.
- **H2, language:** only Hindi differs from English (OR 1.74, 1.11–2.72, Holm p = 0.046), and
  not when restate-only traces count as Level 2 (Holm p = 0.073). Chinese 0.97, Malayalam 0.71,
  both n.s.
- **H3, hint type:** no difference (expert vs. leaked OR 0.76, metadata vs. leaked 1.04, both n.s.).
- **Subject area:** humanities traces admit the hint more often than STEM (OR 1.62, 1.17–2.25,
  Holm p = 0.004).
- **Model × language interaction:** not significant (χ² = 4.51, 6 df, p = 0.608).

## H4: English hint inside a non-English question (`h4.md`)

- **Influence:** the English and own-language expert hints differ in 1 of 9 model × language
  cells: R1-Distill in Malayalam, where the English hint moves more answers (127 vs. 86,
  Holm p < 0.001).
- **Admission:** differs in 1 of 9 cells, again R1-Distill in Malayalam (68.4% vs. 34.5% admitted,
  Holm p < 0.001).

## Reasoning language (`language_subject.md`, `figures/reasoning_language.svg`)

- **The Groq models reason in English** on almost every non-English question: gpt-oss-20b stays
  in the question's language in 1.6% of Hindi, Chinese and Malayalam traces, qwen3.8-27b in 6.0%
  (all Chinese). R1-Distill reasons in Chinese on every Chinese question and on 23% of Hindi ones.
- **Switching and admission:** traces that switch away from the question's language are not
  significantly less faithful (GEE OR 0.84, 95% CI 0.47–1.50, p = 0.56). Few traces stay in the
  question's language, so this comparison is weak.

## Judge reliability

- **Second judge (qwen3.8-27b) on the 338-trace sample:** κ = 0.68 (95% CI 0.58–0.77; 88.8%
  agreement, n = 329) on Level 2 vs. not, and κ = 0.72 on the loose measure
  (`labels/human/main/agreement.csv`). This shows the two judges are consistent, not that they
  are correct.
- **Keyword-filter flags:** 98 F1 (judge Level 0 with a strong keyword hit), 30 F2 (judge Level 2
  with no hit) and 29 Q (quote not found in the trace) among the current labels. The review list
  is `labels/gpt-oss-120b/review_sample.csv`.
- **Flag review:** on the first 11 flagged traces (`labels/gpt-oss-120b/flag_review.csv`), 9 of
  the 10 F1 cases quote the hint and use it, so the judge's rare Level 0 labels are mostly wrong.
  These verdicts are drafts until a team member confirms them; the main tables use the judge's
  levels.
- **No human labels** were collected, so the human-labels-only check was not run.

## Limitations

- qwen3.8-27b is missing shard 6/7 (42 of 300 questions).
- Faithfulness rests on one LLM judge, checked against a second judge and the keyword filter,
  not against human labels.
- The Chinese and Malayalam keyword lists were not reviewed by a native speaker.
