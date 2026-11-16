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
| R1-Distill main run (6,900 runs) | notebook above | Waits for the Malayalam review (`make_conditions.py --require-reviewed`) |
| Groq shard 3/7 (gpt-oss-20b, qwen3.8-27b) | `scripts/run_groq.py` | To do, same wait |

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
