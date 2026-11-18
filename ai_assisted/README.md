# AI-assisted material (declared AI use)

**Everything in this folder was produced with an AI assistant: Claude (Anthropic), used through
Claude Code.** It is kept apart from the study's data and results on purpose:

- None of it is read by any script in `scripts/` or `src/`. Nothing in `results/` or the report's
  numbers depends on it.
- It is not in `labels/`, so `agreement.py`, `rates.py`, `regression.py` and the other analysis
  scripts never treat it as a judge or a human rater.
- The study's faithfulness levels come only from the gpt-oss-120b judge (`labels/gpt-oss-120b/`).

The tested models (gpt-oss-20b, qwen3.8-27b, R1-Distill-Llama-8B) and the LLM judges are part
of the method, not AI assistance, so they are not listed here. Other AI-assisted work is listed in
[`docs/ai_use.md`](../docs/ai_use.md).

## Contents

| Folder | What it is | Who asked for it |
|---|---|---|
| [`shard7_claude_label_check/`](shard7_claude_label_check/) | An AI cross-check of faithfulness: Claude assigned Level 0/1/2 to the 226 influenced shard 7/7 traces (gpt-oss-20b, qwen3.8-27b) using `docs/scoring_guide.md`. Then it was compared with the gpt-oss-120b judge. The folder holds the labels, the comparison and the code that made them. | Sashwath Swaminathan (sub-team D) |
