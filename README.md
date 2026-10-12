# Truthful Representations of Reasoning

A hint-insertion audit of chain-of-thought faithfulness in English, Hindi, Chinese and Malayalam.


We add a hint pointing to a wrong option to MMLU questions and measure how often three
open-weight reasoning models (gpt-oss-20b, Qwen3-32B, DeepSeek-R1-Distill-Llama-8B)
admit in their reasoning that the hint changed their answer.

## Setup

```bash
uv sync                 # Python >= 3.11
cp .env.example .env    # add your Groq key(s): GROQ_API_KEY_1, GROQ_API_KEY_2, ...
uv run pytest
```

## Pipeline

| Step | Command | Output |
|---|---|---|
| 1. Select and match questions | `uv run python scripts/build_dataset.py` | `data/questions.jsonl`, `data/reserve.jsonl`, `data/manifest.json`, `data/review/ml_review_60.csv` |
| 2. Render all prompts | `uv run python scripts/make_conditions.py` | `data/conditions.jsonl` (6,900 prompts, same for every model) |
| 3a. Run Groq models | `uv run python scripts/run_groq.py --model qwen3-32b` | `runs/qwen3-32b/<date>.jsonl` |
| 3b. Run the Kaggle model | see `scripts/run_vllm.py` docstring | `runs/r1-distill-llama-8b/<date>.jsonl` |
| Smoke test | `uv run python scripts/smoke_test.py --n 3` | `runs/smoke/...` |

Steps 1 and 2 are deterministic: the seed, dataset revisions and hashes are in
`configs/experiment.yaml` and `data/manifest.json`.

Run scripts take filters (`--n-questions`, `--langs`, `--hint-types`, `--no-h4`, `--limit`) and
**resume automatically**: a condition already logged for that model is skipped, and failed calls
(logged in `runs/<model>/errors.jsonl`) are retried on the next run. When every Groq key hits its
rate limit, the script stops cleanly. Run it again later to continue.

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

## Open review tasks (sub-team A)

1. **Malayalam questions**: fill `verdict` in `data/review/ml_review_60.csv`. Add the qid of every
   bad question to `configs/excluded_questions.txt` and rerun steps 1–2; each excluded question is
   replaced by the next reserve question from the same stratum.
2. **Hint and instruction translations**: hi / zh / ml text in `configs/hints.yaml` is a draft
   (`reviewed: false`). Native speakers check hi and ml; zh is checked by back-translation. Set
   `reviewed: true` and add `reviewed_by` when done. `make_conditions.py` lists unreviewed entries;
   use `--require-reviewed` for the main runs.

## Run log format

One JSON object per line: `run_id`, `model`, `model_id`, `model_returned`, `provider`,
`timestamp_utc`, `params`, the condition fields (`condition_id`, `qid`, `lang`, `hint_type`,
`hint_lang`, `rep`, `gold`, `hinted`, `subject`, `stratum`, `prompt_sha256`), `reasoning`,
`content`, `answer` (extracted letter or null), `finish_reason` (`length` = hit the 4,096 + 512
token cap), `usage`, `latency_s`, `key_alias` (never the key itself).

## Layout

```
configs/      experiment.yaml (seed, models, sampling), hints.yaml (prompt text), excluded_questions.txt
src/cotaudit/ data loading/matching/selection, prompts, conditions, answer extraction, run log, runners
scripts/      build_dataset, make_conditions, run_groq, run_vllm, smoke_test
data/         built dataset and prompts (committed)
runs/         every model run (committed)
tests/
```
