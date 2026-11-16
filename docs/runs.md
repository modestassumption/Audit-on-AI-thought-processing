# Model runs: Kaggle model and answer extraction

**Owner:** Sanjay Rajkumar (2024A8PS2044H), sub-team B. Proposal §4.3, §4.5 and §5: running the
Kaggle model (vLLM) and answer extraction. Groq shard 3/7 in [`compute.md`](compute.md).

| Work | Code | Status |
|---|---|---|
| Answer extraction: multilingual answer forms, full-width text, R1-style `\boxed{}` answers, no lower-case false matches | `src/cotaudit/extract.py`, `tests/test_extract.py` | Done and tested (below) |
| Extraction check on logged runs, with a hand-check sheet | `scripts/check_extraction.py`, `tests/test_check_extraction.py` | Done. On the October smoke runs: 15/15 extracted, all from `Answer: X` |
| vLLM run script: time limit per session, GPU-memory options, GPU hours printed | `scripts/run_vllm.py`, `src/cotaudit/runners/vllm_runner.py`, `tests/test_run_vllm.py` | Done and tested with a stand-in model (no GPU) |
| Kaggle notebook for R1-Distill-Llama-8B | `notebooks/kaggle_r1_distill.ipynb` | Ready to run |
| R1-Distill pilot (50 questions, 1,150 runs) and main run (6,900 runs) on Kaggle T4 x2 | notebook above | To do. Main run waits for the Malayalam review (`make_conditions.py --require-reviewed`) |
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
