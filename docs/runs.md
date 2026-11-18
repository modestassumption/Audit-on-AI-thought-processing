# Model runs: Kaggle model and answer extraction

**Owner:** Sanjay Rajkumar (2024A8PS2044H), sub-team B. Proposal §4.3, §4.5 and §5: running the
Kaggle model (vLLM) and answer extraction. Groq shard 3/7 in [`compute.md`](compute.md).

| Work | Code | Status |
|---|---|---|
| Answer extraction: multilingual answer forms, full-width text, R1-style `\boxed{}` answers, no lower-case false matches | `src/cotaudit/extract.py`, `tests/test_extract.py` | Done and tested (below) |
| Extraction check on logged runs, with a hand-check sheet | `scripts/check_extraction.py`, `tests/test_check_extraction.py` | Done. On the October smoke runs: 15/15 extracted, all from `Answer: X` |
| vLLM run script: time limit per session, GPU-memory options, GPU hours printed | `scripts/run_vllm.py`, `src/cotaudit/runners/vllm_runner.py`, `tests/test_run_vllm.py` | Done and tested with a stand-in model (no GPU) |
| Kaggle notebook for R1-Distill-Llama-8B | `notebooks/kaggle_r1_distill.ipynb` | Ready to run |
| Runs logged before the dataset or a prompt changed: redo them, leave them out of the analysis | `src/cotaudit/runners/base.py`, `src/cotaudit/runlog.py`, `src/cotaudit/analysis/influence.py`, `tests/test_stale_runs.py` | Done and tested (below) |
| Tokenizer fix: tokenize prompts and decode outputs from tokenizer.json, check all four languages before the model loads | `src/cotaudit/runners/vllm_runner.py`, `tests/test_run_vllm.py` | Done (below) |
| R1-Distill pilot (50 questions, 1,150 runs) on Kaggle T4 x2 | `runs/r1-distill-llama-8b/2026-11-16-kaggle.jsonl`, `results/r1_pilot.md` | Done Nov 16 (2.24 GPU hours, with the tokenizer fix; a first attempt was unusable, below). All 1,150 runs match `data/conditions.jsonl`. Answers extracted: en 90%, hi 96%, ml 96%, zh 83%; every miss is a run cut off at the 4,096-token reasoning cap (zh 17%). Baseline accuracy en 81%, zh 61%, hi 52%, ml 41%. Influence over same-language hints about 26% (126/484 determined runs), above the 15% pilot rule |
| R1-Distill main run (6,900 runs) | notebooks above, `runs/r1-distill-llama-8b/2026-11-16-kaggle-main-{a,b}.jsonl`, `runs/r1-distill-llama-8b/2026-11-17-kaggle-topup.jsonl`, `results/r1_main.md` | **Done.** Main runs Nov 16 on Kaggle T4 x2 (A: en+hi, 2,750 runs, 5.9 h; B: zh+ml, 3,000 runs, 7.1 h, in parallel). The Malayalam review (Nov 17) replaced questions, so a top-up (`notebooks/kaggle_r1_topup.ipynb`, Nov 17) ran the 437 conditions of 19 questions that changed. All 6,900 conditions of the current `data/conditions.jsonl` now have a run with the current prompt; no run has byte-level tokens. Answers extracted: en 88%, hi 92%, ml 94%, zh 81%; misses are runs cut off at the 4,096-token cap. The 437 superseded runs stay in the logs and are left out by `load_runs()` |
| Groq shard 3/7 (gpt-oss-20b, qwen3.8-27b) | `scripts/run_groq.py`, `runs/gpt-oss-20b/2026-11-11-sanjay.jsonl`, `runs/qwen3.8-27b/2026-11-11-sanjay.jsonl`, then `runs/<model>/2026-11-1{7,8}-sanjay-colab.jsonl` and `2026-11-18-sanjay-groq.jsonl` | **Done.** All 1,219 conditions of shard 3/7 have a current run for both models. Nov 11 session on Sanjay's key (gpt-oss-20b 207 runs, 180 current; qwen3.8-27b 148, 134 current), then Colab and Groq sessions on Nov 17–18. Runs on the dropped `high_school_psychology/test/313` or on hints reworded in review stay in the logs and are left out by `load_runs()` |
| R1-Distill judge labels (gpt-oss-120b) | `scripts/run_judge.py --judge gpt-oss-120b --models r1-distill-llama-8b --tag sanjay` (Groq), `scripts/run_judge_deepinfra.py --models r1-distill-llama-8b` (DeepInfra), `labels/gpt-oss-120b/2026-11-18-sanjay.jsonl`, `labels/gpt-oss-120b/2026-11-18-sanjay-deepinfra.jsonl` | **Done: all 909** influenced, non-truncated R1 traces have a current gpt-oss-120b label. 507 on Groq (Nov 18, team keys, free tier; level 0: 179, 1: 107, 2: 221; 4 `needs_manual`), 82 more in teammates' Groq label files, and the last 320 on **DeepInfra** (Nov 18, same model `openai/gpt-oss-120b`, same prompt, parsing, keywords and judging order; level 0: 123, 1: 54, 2: 143; 6 `needs_manual`; $0.044), after every Groq key hit its 200K tokens-per-day cap. DeepInfra labels record `provider: deepinfra`; Groq labels have no `provider` field. 73 traces have a second Groq label in another file; `load_labels()` keeps the first by file name. No DeepInfra-labelled trace has another label. Sub-team C to note the provider in the judge section |

## Run

```bash
uv run python scripts/check_extraction.py                    # table + results/extraction/failures.csv
uv run python scripts/check_extraction.py --sample 10        # also results/extraction/hand_check.csv
uv run python scripts/check_extraction.py --score results/extraction/hand_check.csv
uv run pytest tests/test_extract.py tests/test_check_extraction.py tests/test_run_vllm.py
```

On Kaggle, open `notebooks/kaggle_r1_distill.ipynb` (File → Import Notebook) and run it top to
bottom. It runs the pilot, checks extraction, then the main run, which stops after 11 hours
(`--max-hours`) and continues next session. Download `runs_r1.zip` at the end and push
`runs/r1-distill-llama-8b/` from your machine.

## Answer extraction

Only the answer section is read (for R1, the text after `</think>`), never the reasoning. The
text is NFKC-normalised first, so `答案：Ｃ` reads like `答案:C`. Rules, highest priority first;
within a rule the last match wins:

1. **label:** `Answer: X`, the form every prompt asks for, also `Final answer`, `**Answer:** (C)`,
   `Answer: $B$` and the label in Hindi, Chinese or Malayalam.
2. **boxed:** `\boxed{C}`, `\boxed{(C)}`, `\boxed{\text{C}}`, `\boxed{C. ...}`, which R1-Distill
   often writes.
3. **phrase:** "the answer is (C)", "the correct option is D", `答案是C`, `我选C`, `उत्तर (B) है`,
   `ഉത്തരം (A) ആണ്`.
4. **bare:** a lone letter on the last line.

Letters must be capitals unless bracketed: the old extractor read "the answer is a bit unclear"
as A. A capital followed by CJK text now counts (`答案：C选项` gave no answer before, because
there is no word boundary between C and 选).

`check_extraction.py` reports, per model and language: letters found, which rule found them
(the share via `label` is how well the model follows the format), runs cut off by the token cap,
runs that give two different committed answers (`Answer:` or `\boxed`; quoted hints like "the
professor says the answer is (C)" don't count), and runs whose logged `answer` differs from the
current extractor's, which happens if a log was written before this change.

## When the dataset or a prompt changes

A run is identified by model + question + language + hint + repeat, which doesn't include the
prompt text. So when a question is replaced, or a reviewed translation changes a hint or the
instruction, old logs could be reused for the new prompt. Two checks prevent that:

- **Running:** `run_vllm.py` and `run_groq.py` count a run as done only if it was logged with the
  condition's current `prompt_sha256` (`RunLog.completed_prompts()`), so changed prompts run again.
  Logs with no hash still count by id.
- **Analysis:** `load_runs()` leaves out runs in `runs/` whose question is no longer in
  `data/conditions.jsonl` or whose prompt has changed, and prints how many on stderr. Other
  folders (test fixtures) aren't filtered unless `current=` is passed.

The 50-question R1 pilot was run on the October grid. Replayed against the rebuilt
`data/questions.jsonl` (Nov 15, with a placeholder for the missing `jurisprudence` subject
name), 764 of its 1,150 runs still match; 386 are left to run (368 for 16 questions new to the
first 50, and 18 Hindi/Chinese expert hints whose subject names changed in review). Runs for the
14 dropped questions are ignored. When the Malayalam review lands, the Malayalam runs change the
same way and are redone automatically.

## Tokenizer bug in the first Kaggle pilot (2026-11-16)

The notebook installs the newest vLLM (0.33.0 that day). With it, the tokenizer built for
DeepSeek-R1-Distill-Llama-8B dropped all non-ASCII text from prompts and returned byte-level
tokens instead of text (`ĊĊAnswer:ĠD`). A 405-character Hindi prompt reached the model as 23
tokens; the model saw only the instruction's "Answer: X" and the option letters, and its baseline
accuracy was 13% (hi), 5% (zh) and 17% (ml), below the 25% of guessing. English prompts survived
(73% accuracy), but the whole pilot is rerun so every language uses the same tokenizer.

Fix: `VLLMRunner` encodes prompts and decodes outputs with the `tokenizers` library straight from
the model's tokenizer.json and passes token ids to vLLM. Before the model loads it round-trips a
hint sentence in each language and stops if any text changes. `check_extraction.py` reports runs
with byte-level tokens in their text (`undecoded tokens`) and warns.
