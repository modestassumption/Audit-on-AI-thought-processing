# Team setup: Groq keys, local runs, Kaggle

Every member does **Part 1 and 2** (about 15 minutes). Sanjay plus one backup do **Part 3**.

## Part 1: Get a Groq API key

1. Open <https://console.groq.com> and sign up with **your own** email, Google or GitHub account.
   The free tier's limits apply per account, so each member's key adds capacity.
2. In the left menu open **API Keys** and click **Create API Key**. Name it `cotaudit-<yourname>`.
3. Copy the key (it starts with `gsk_`) right away, because it is only shown once. Keep it private:
   don't paste it into chat, a commit or a shared doc.
4. Open **Settings → Limits**. Copy the RPM / RPD / TPM / TPD values for these three models into
   [`compute.md`](compute.md) (one row per model; everyone should see the same numbers, but check):
   `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-120b`.

## Part 2: Set up the repo and check your key

```bash
git clone https://github.com/modestassumption/Audit-on-AI-thought-processing.git
cd Audit-on-AI-thought-processing
pip install uv                      # or see https://docs.astral.sh/uv/getting-started/installation/
uv sync
cp .env.example .env                # then edit .env: GROQ_API_KEY_<YOURNAME>=gsk_...
uv run pytest
uv run python scripts/smoke_test.py --n 1 --langs en
```

The smoke test should print `reasoning returned : 5/5` and `answer extracted : 5/5` for both
models. Smoke runs go to `runs/smoke/`, which is not part of the experiment.

### Running your share of the experiment

Each member gets a shard number (1–7, listed in [`compute.md`](compute.md)) and runs only their
share, on their own key and machine:

```bash
uv run python scripts/run_groq.py --model gpt-oss-20b --n-questions 50 --shard 3/7   # pilot
uv run python scripts/run_groq.py --model qwen3.8-27b --n-questions 50 --shard 3/7
```

- Logs go to `runs/<model>/<date>-<computer-name>.jsonl`, so nobody's files collide. Use
  `--tag <yourname>` if you want a different suffix.
- When every key you have is rate-limited the script stops cleanly. **Run the same command
  again later** and it continues where it stopped; failed calls are retried automatically.
- Commit and push your `runs/` files when you stop (`git add runs && git commit && git pull --rebase && git push`).
- Do not start pilot or main runs until the reviewed hint translations are merged
  (`uv run python scripts/make_conditions.py --require-reviewed` passes on `main`).

## Part 3: Kaggle (R1-Distill-Llama-8B with vLLM)

1. Create a Kaggle account and complete **Settings → Phone verification**. GPUs and internet
   access are disabled until you do.
2. **Create → New Notebook**. In the right-hand panel set **Accelerator: GPU T4 x2** and turn
   **Internet** on.
3. In the first cell:
   ```
   !git clone https://github.com/modestassumption/Audit-on-AI-thought-processing.git
   %cd Audit-on-AI-thought-processing
   !pip install -q -e ".[kaggle]"
   !python scripts/run_vllm.py --model r1-distill-llama-8b --tp 2 --dtype half --n-questions 50 --tag kaggle
   ```
   If installing vLLM breaks Kaggle's preinstalled PyTorch, try an older vLLM release and record
   the version that works in `pyproject.toml`.
4. Results are written in batches, so a timeout loses at most one batch. Before the session ends,
   download `runs/r1-distill-llama-8b/` from the **Output** panel (or zip it with
   `!zip -r runs.zip runs/r1-distill-llama-8b`) and commit it from your machine.
5. Kaggle allows about 30 GPU hours per week per account. Note the hours each session used in
   [`compute.md`](compute.md).
