#!/usr/bin/env bash
# Regenerate every table and figure in results/ from the runs and judge labels on disk.
# Run from the repo root after the final labels are merged:   bash scripts/regenerate_results.sh
# Order follows docs/analysis.md ("Run"). The human-labels-only check is skipped: no human labels.
set -euo pipefail
export PYTHONIOENCODING=utf-8
run() { echo "== $*"; uv run python "$@"; }

run scripts/report_runs.py --out results/runs.md
run scripts/report_runs.py --models r1-distill-llama-8b --out results/r1_main.md
run scripts/sample_size.py --out results/sample_size.md
run scripts/report_stats.py --out results/stats.md
run scripts/rates.py --out results/rates.md
run scripts/rates.py --measure loose --out results/rates_loose.md
run scripts/regression.py --out results/regression.md
run scripts/regression.py --restate-as-admitted --out results/regression_restate.md
run scripts/h4.py --out results/h4.md
run scripts/language_subject.py --out results/language_subject.md
run scripts/figures.py
run scripts/agreement.py --name main
run scripts/run_judge.py --judge gpt-oss-120b --review-sample
uv run pytest -q
echo "Done. Check git diff --stat results/ labels/human/main/agreement.csv"
