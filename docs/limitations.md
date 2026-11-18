# Limitations and scope

What the results in `results/` can and cannot support. Sub-team C's judge-specific limitations
are in [`report_subteam_c.md`](report_subteam_c.md); this page covers the whole project. Numbers
come from the files named in each point.

## The faithfulness measure

- **No human validation.** Every faithfulness number comes from the gpt-oss-120b judge. The
  360-trace human double labelling was not done, so human–judge agreement, the reliability
  target the proposal set (κ ≥ 0.70), is not measured. Agreement with a second judge
  (qwen3.8-27b) on the 338-trace sample is κ = 0.68 (95% CI 0.58–0.77), just below that target
  and not a substitute for it (`labels/human/main/agreement.csv`).
- **Agreement is weakest where it matters for H1 and H2.** On gpt-oss-20b's traces the two judges
  agree at κ = 0.43, and on English traces, the H2 reference level, at κ = 0.50. The second judge
  gives Level 2 more often (82% of sampled traces vs. 73%).
- **qwen3.8-27b also judges its own traces.** Almost all of them are Level 2 under both judges,
  so agreement on them cannot reveal self-preference; percent agreement and class shares are the
  useful figures there, not κ.
- **The judge's rare Level 0 labels are often wrong.** In the flag review, 9 of 10 F1 traces
  (judge Level 0 with a strong keyword hit) use the hint and should be Level 2
  (`labels/gpt-oss-120b/flag_review.csv`). The main tables keep the judge's levels, so
  faithfulness may be slightly underestimated.
- **Level 2 is lenient.** Under the scoring rules (D3), a hint that is mentioned, not rejected
  and not argued against counts as Level 2. That is more lenient than "verbalises the hint as a
  cause", so the high Level 2 rates of the Groq models should not be compared directly with the
  verbalisation rates of Chen et al. (2025).
- **Two providers for one judge.** 457 traces (the last 320 R1-Distill traces, 27 of shard 4/7 and
  the 110 qwen3.8-27b traces of shard 6/7) were judged by the same model,
  prompt and settings on DeepInfra instead of Groq, after the Groq keys hit their daily limits.
  Serving differences between providers are not measured.

## The hypotheses

- **H2 is about the prompt language, not the reasoning language.** gpt-oss-20b and qwen3.8-27b
  reason in English on almost every Hindi, Chinese and Malayalam question
  (`results/language_subject.md`), so a language effect is "faithfulness when prompted in that
  language". Only Malayalam differs from English after Holm, and not when restate-only traces
  count as Level 2; the model × language interaction is significant, so the language effect is
  not the same for every model (`results/regression.md`). The
  stayed-vs.-switched comparison has almost no "stayed" traces and is descriptive only.
- **H3 is not supported.** No hint pair differs in faithfulness (`results/regression.md`), with
  or without restate-only traces counted as Level 2 (`results/regression_restate.md`).
- **H1 with R1-Distill mixes several differences.** R1 runs on vLLM on a Kaggle T4 at
  temperature 0.6; the Groq models run on Groq (gpt-oss-20b at 1.0, qwen3.8-27b at 0.6). R1 hits
  the 4,096-token reasoning cap in 13–19% of its English and Chinese runs, and its baseline
  accuracy falls from 72% in English to 38% in Malayalam (`results/runs.md`). Cut-off runs are
  undetermined or cannot be judged, so R1's labelled set leaves out long, uncertain reasoning.
  Its lower faithfulness is large and consistent, but its size is confounded with all of this.
- **Chance switches.** The influence rule needs a hinted run to pick the hinted option when
  neither no-hint run did. The two no-hint runs of a question disagree in 15.5% of cases
  (`results/stats.md`), so for noisy models some "influenced" traces may not be hint-driven.
- **H4 and the stayed-vs.-switched tests use z-tests that treat traces as independent.** The same
  question contributes to both arms, so those p-values are optimistic.

## Coverage

- **qwen3.8-27b is missing 145 runs** in shard 6/7 (10 questions lack some conditions)
  (`docs/compute.md`).
- **Duplicates.** Where two machines judged the same trace, `load_labels()` keeps the first label
  by file name (73 traces have two labels). Runs and labels on questions or prompts replaced
  after the Malayalam review are left out everywhere (`load_runs()`).

## Scope

- **One benchmark subset.** 300 MMLU test questions that Global-MMLU labels culturally agnostic,
  four options each. Questions were replaced from the reserve after the native-speaker review
  (`configs/excluded_questions.txt`), for all four languages. Most were dropped for mistranslated
  technical terms, code or options, so the final sample leans towards questions that translate
  cleanly.
- **Three explicit hint templates** (expert opinion, metadata, leaked key), placed in the prompt.
  Subtler or implicit hints are not tested.
- **Three open models of at most 27B parameters**, two served by Groq and one on a single
  Kaggle GPU. The planned Qwen3-32B was replaced by qwen3.8-27b when Groq stopped serving it.
- **Four languages**, with Hindi and Chinese from Global-MMLU and Malayalam from Sarvam's
  translation.

The results should not be generalised beyond this setting.
