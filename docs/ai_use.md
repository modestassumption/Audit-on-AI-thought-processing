# AI-use declaration

This page lists the work in this repository that an AI assistant (Claude, Anthropic, via Claude
Code) drafted or carried out, so it can be copied into the report's AI-use declaration. It covers
only what the repository records: commits whose message ends in a `Co-Authored-By: Claude`
line, and files that say they were Claude-drafted. **Each member should add any other AI use in
their own work before submission.** The LLM judge (gpt-oss-120b) and the tested models are part
of the method, not assistance, and are described in the methods section.

## Drafted by Claude, checked and accepted by a team member

| Work | Where | Checked by |
|---|---|---|
| Malayalam question review: verdicts and notes on the 60-question sample (13 marked bad) | `data/review/ml_review_60.csv` (`reviewer` column) | Visakh V Menon (native speaker) accepted the drafts |
| Notes on the Hindi and Malayalam prompt text (instructions, hints, subject names) | `docs/translation_review.md` | Hindi: Yash Agarwal reviewed the text directly. Malayalam: Visakh V Menon accepted the notes |
| Chinese prompt check by back-translation | `docs/translation_review.md` | Compared against the English source text |
| Review of the traces flagged by the keyword filter (F1/F2) | `labels/gpt-oss-120b/flag_review.csv` | Draft verdicts; a team member must confirm them |

## Code, runs and analysis carried out with Claude

All by Visakh V Menon's sub-team A, with Claude as co-author (`git log --grep "Co-Authored-By: Claude"`):

- **Malayalam data quality:** a structural screen for passages, premises and formulas dropped in
  translation (`src/cotaudit/data/screen.py`), and review verdicts kept across dataset rebuilds
  (`src/cotaudit/data/review.py`).
- **Pipeline maintenance:**
  - merging the sub-team branches;
  - counting only judge and human labels that belong to current traces (`analysis/influence.py`,
    `scripts/agreement.py`, `analysis/regression.py`);
  - the "human labels only" robustness check;
  - a test fix in `run_vllm`.
- **Shard 1/7:** smoke test, gpt-oss-20b and qwen3.8-27b runs (805 each), and judge labels. The
  runs and labels themselves come from the models; Claude ran the scripts.
- **Results and documents:**
  - generating `results/` with sub-team D's scripts;
  - the changes-from-proposal list in `README.md`;
  - the Kaggle hours log;
  - this page.
