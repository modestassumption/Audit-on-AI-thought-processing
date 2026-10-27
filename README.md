# Truthful Representations of Reasoning

A hint-insertion audit of chain-of-thought faithfulness in English, Hindi, Chinese and Malayalam.


We add a hint pointing to a wrong option to MMLU questions and measure how often three
open-weight reasoning models (gpt-oss-20b, Qwen3.8-27B, DeepSeek-R1-Distill-Llama-8B)
admit in their reasoning that the hint changed their answer.

Groq stopped serving Qwen3-32B and Llama-3.3-70B, both named in the proposal. On 2026-10-28 we
switched to `qwen/qwen3.8-27b` as the tested Qwen model and as the second judge
(`configs/experiment.yaml`).

## Setup

```bash
uv sync                 # Python >= 3.11
cp .env.example .env    # add your Groq key: GROQ_API_KEY_<YOURNAME>=gsk_...
uv run pytest
```

New team member? Follow [`docs/setup.md`](docs/setup.md) (Groq key, smoke test, your shard, Kaggle).

## Pipeline

| Step | Command | Output |
|---|---|---|
| 1. Select and match questions | `uv run python scripts/build_dataset.py` | `data/questions.jsonl`, `data/reserve.jsonl`, `data/manifest.json`, `data/review/ml_review_60.csv` |
| 2. Render all prompts | `uv run python scripts/make_conditions.py` | `data/conditions.jsonl` (6,900 prompts, same for every model) |
| 3a. Run Groq models | `uv run python scripts/run_groq.py --model qwen3.8-27b --shard 3/7` | `runs/qwen3.8-27b/<date>-<tag>.jsonl` |
| 3b. Run the Kaggle model | see `scripts/run_vllm.py` docstring | `runs/r1-distill-llama-8b/<date>-<tag>.jsonl` |
| 4. Health, influence, quota | `uv run python scripts/report_runs.py --out results/pilot.md` | `results/*.md` |
| 5. Judge influenced traces | `uv run python scripts/run_judge.py --judge gpt-oss-120b` | `labels/gpt-oss-120b/<date>-<tag>.jsonl` |
| 6. Human labelling set | `uv run python scripts/export_labelling.py --name main --per-cell 30` | `labels/human/main/items.csv`, `key.csv` |
| 7. Agreement (kappa) | `uv run python scripts/agreement.py --name main` | printed table |
| Smoke test | `uv run python scripts/smoke_test.py --n 3` | `runs/smoke/...` |

Steps 1 and 2 are deterministic: the seed, dataset revisions and hashes are in
`configs/experiment.yaml` and `data/manifest.json`.

Run scripts take filters (`--n-questions`, `--langs`, `--hint-types`, `--no-h4`, `--limit`,
`--shard i/n`) and **resume automatically**: a condition already logged for that model is skipped, and failed calls
(logged in `runs/<model>/errors-<tag>.jsonl`) are retried on the next run. When every Groq key hits its
rate limit, the script stops cleanly. Run it again later to continue.

- `--n-questions N` takes the first N questions in a seeded order that alternates the two strata,
  so `--n-questions 50` is the balanced 25 + 25 pilot and `--n-questions 250` is the fallback
  size. Pilot runs are ordinary runs of the main grid and count toward it.
- `--shard i/n` gives each team member a disjoint share of the questions to run on their own key.
  Logs are named `<date>-<tag>.jsonl` (tag defaults to the computer name), so members' files never
  conflict; a run logged by anyone is skipped by everyone once pushed.
- A hinted run is **influenced** if it picks the hinted option and neither no-hint run did
  (`src/cotaudit/analysis/influence.py`); faithfulness is labelled only on those runs, following
  [`docs/scoring_guide.md`](docs/scoring_guide.md).

## Data

- **300 questions**: 150 STEM + 150 Humanities/Social Sciences, drawn at random (seed 21) from
  MMLU test questions that Global-MMLU labels culturally agnostic (`CA`).
- **en** from MMLU (`cais/mmlu`); **hi, zh** from Global-MMLU (`sample_id` joins directly);
  **ml** from Sarvam `mmlu-indic`. Sarvam has no ids, but its `en` and `ml` configs are
  row-aligned, so each Malayalam row is matched by finding its Sarvam-English twin in MMLU by
  normalised text. A question is kept only if the answer key agrees in all sources.
- **Hinted answer**: one wrong option per question, fixed across hint types, languages and models.

### Conditions per question (23 → 6,900 per model)

| | per language | languages | total / question |
|---|---|---|---|
| No hint (×2) | 2 | en, hi, zh, ml | 8 |
| Expert / metadata / leaked hint, in the question's language | 3 | en, hi, zh, ml | 12 |
| H4: English expert hint inside a non-English question | 1 | hi, zh, ml | 3 |

## Open review tasks

1. **Malayalam questions**: fill `verdict` in `data/review/ml_review_60.csv`. Add the qid of every
   bad question to `configs/excluded_questions.txt` and rerun steps 1–2; each excluded question is
   replaced by the next reserve question from the same stratum.
2. **Hint and instruction translations**: hi / zh / ml text in `configs/hints.yaml` is a draft
   (`reviewed: false`). Native speakers check hi and ml; zh is checked by back-translation. Set
   `reviewed: true` and add `reviewed_by` when done. `make_conditions.py` lists unreviewed entries;
   use `--require-reviewed` for the main runs.
3. **Keyword lists** (sub-team C + native speakers): extend hi / zh / ml terms in
   `configs/keywords.yaml` from pilot traces and set `reviewed: true`.
4. **Groq limits and shard owners**: fill in [`docs/compute.md`](docs/compute.md).

## Run log format

One JSON object per line: `run_id`, `model`, `model_id`, `model_returned`, `provider`,
`timestamp_utc`, `params`, the condition fields (`condition_id`, `qid`, `lang`, `hint_type`,
`hint_lang`, `rep`, `gold`, `hinted`, `subject`, `stratum`, `prompt_sha256`), `reasoning`,
`content`, `answer` (extracted letter or null), `finish_reason` (`length` = hit the 4,096 + 512
token cap), `usage`, `latency_s`, `key_alias` (never the key itself).

## Layout

```
configs/      experiment.yaml (seed, models, judges), hints.yaml (prompt text), keywords.yaml,
              judge_prompt.md, excluded_questions.txt
src/cotaudit/ data loading/matching/selection, prompts, conditions, answer extraction, run log, runners,
              analysis (influence, agreement), judge (keywords, LLM judge)
scripts/      build_dataset, make_conditions, run_groq, run_vllm, smoke_test, report_runs,
              run_judge, export_labelling, agreement
docs/         setup.md (team onboarding), compute.md (limits, shards), scoring_guide.md
data/         built dataset and prompts (committed)
runs/         every model run (committed)
labels/       judge labels and human labelling sets (committed)
results/      generated reports
tests/
```
