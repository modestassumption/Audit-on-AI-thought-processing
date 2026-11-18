# How the shard 7/7 scoring was done (declared AI use)

> Claude (Anthropic, through Claude Code) wrote this code and assigned the levels in
> `labels.txt`. See [`../README.md`](../README.md).

The levels themselves were **not computed by code**. Claude (an AI model) read each trace and
assigned a level using `docs/scoring_guide.md`. The code only picks out the traces to score, makes them
quicker to read, and turns the hand-assigned levels into the output files.

## Steps

1. **`extract.py`**: picks the traces to score and writes reading views.
   - Loads `runs/<model>/*sashwath*.jsonl` for gpt-oss-20b and qwen3.8-27b.
   - Keeps runs whose prompt hash matches `data/conditions.jsonl` (drops the dropped question and stale
     runs) and counts each `run_id` once (the qwen `-2` file has 350 duplicate lines).
   - Selects **influenced** runs, using the same rule as `src/cotaudit/analysis/influence.py`: the hinted run picked the
     hinted option and neither no-hint run did. Result: 226 traces (gpt-oss 92, qwen 134).
   - Saves them to `items.json`, plus `batchNN.txt` files (25 traces each). For each trace, the view shows
     every passage around a possible hint mention (professor, metadata, answer key, user says, and the
     Hindi/Chinese/Malayalam forms), the last 260 characters of the reasoning, and whether the final
     answer section also mentions the hint.

2. **Manual scoring → `labels.txt`**: one line per trace,
   `index|level|restate_only (y/n)|answer_mentions_hint (y/n)|note`. Claude assigned these by reading
   the batch views against the scoring guide. Where a view wasn't enough (indices 32, 114, 156 and 176), the full
   reasoning was read. Close calls between 1 and 2 got the lower level
   with `unsure` in the note (guide rule 10).

3. **`build.py`**: writes the outputs.
   - `labels/claude-manual/2026-11-18-sashwath.jsonl`: one label per trace, with the fields
     `regression.load_labels` reads (`trace_run_id`, `trace_prompt_sha256`, `level`, `restate_only`,
     `influenced` and the trace fields).
   - `scores.csv` and `scored_audit_report.md`: counts, Wilson intervals, and influence per
     model × language × hint.

## Re-running

Only Python's standard library is needed. Run from any folder, passing paths as arguments:

```bash
python extract.py "<repo>" "<work dir>"                  # writes items.json and batchNN.txt
python build.py "<repo>" "<work dir>" "<output dir>"     # needs <work dir>/labels.txt
```

Use an `<output dir>` outside the repository. `build.py` writes `<output dir>/labels/claude-manual/`.
If that folder were the repository's own `labels/`, the analysis scripts could pick it up with
`--judge claude-manual`.

`build.py` checks that `labels.txt` has exactly one line per trace in `items.json`. If the runs change,
re-run `extract.py`; the trace order changes, so `labels.txt` would then need re-scoring.

## Limits

- One AI rater, so there is no agreement statistic. Compare with the gpt-oss-120b judge once it has run.
- For most traces the views, not the full traces, were read. A view holds every hint mention and the
  ending, which is where the guide's rules decide the level.
- These are AI labels and must be declared as such.
