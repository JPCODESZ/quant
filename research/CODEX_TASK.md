# Overnight Codex Task

Read `AGENTS.md`, `README.md`, and `research/state.json` before doing anything.

1. Run `python src/load_data.py` and verify the expected row counts and frozen 12-feature list.
2. Run `python scripts/experiment24.py` exactly as written first. Do not modify it before the first run.
3. Record Experiment 24 in `research/EXPERIMENT_LOG.md` and preserve all output tables under `outputs/`.
4. Interpret which feature groups contribute to conditional directional AUC versus resolution AUC.
5. You may then conduct at most THREE additional structural experiments specifically aimed at improving causal directional prediction, following all preregistration rules in `AGENTS.md`.
6. Do not perform hyperparameter sweeps, threshold sweeps, indicator fishing, or iterative tuning based on test-period P&L.
7. Treat 2024-August 2026 as consumed development data.
8. At completion create `research/OVERNIGHT_REPORT.md` containing every experiment, including failures, with leakage audit, sample sizes, year-by-year directional performance, post-hoc observations clearly labeled, and the next candidate for genuinely unseen future validation.

Do not connect to any broker or live trading account. Research and simulation only.
