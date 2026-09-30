# NQ Intraday ML Research

Controlled research repository for the NQ intraday machine-learning project exported from QuantConnect.

## Current status

The current bottleneck is directional prediction, not movement/resolution prediction.

Experiment 23 decomposed the original V2 signal across 32 monthly out-of-sample development windows:

- multiclass macro AUC: 0.5359
- resolution AUC: 0.5771
- conditional direction AUC: 0.5135
- directional accuracy: 51.14%
- resolution AUC exceeded direction AUC in 28 of 32 months

All data through August 2026 is consumed development data and must not be treated as final untouched validation.

## Repository layout

- `AGENTS.md` — rules for Codex and all automated research
- `research/state.json` — frozen project state
- `research/EXPERIMENT_LOG.md` — experiment record
- `src/load_data.py` — data loader
- `scripts/experiment24.py` — next fixed diagnostic
- `data/` — exported QuantConnect datasets
- `outputs/` — generated tables and reports

## Required data files

Upload these exported files into `data/`:

- `v2_ext.csv.gz`
- `model_rows_ext.csv.gz`
- `audit20.csv.gz`
- `wf26_trades.csv.gz`

Then run:

    python -m pip install -r requirements.txt
    python scripts/experiment24.py

Read `AGENTS.md` before changing the research plan.
