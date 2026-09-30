# NQ ML Research — Codex Instructions

You are working on a controlled quantitative research project.

The goal is scientific falsification and robust out-of-time prediction, not manufacturing a profitable backtest.

## Hard rules

1. Research and simulation only. Never connect to a broker, exchange, funded account, or live trading system.
2. Never optimize until a desired win rate, Sharpe, or total return appears.
3. State each hypothesis and falsification criterion before running an experiment.
4. Preserve chronological causality: training -> prior calibration -> future evaluation.
5. Future information may appear only in labels and evaluation.
6. Never use future-confirmed pivots, centered rolling windows, future session highs/lows, or hindsight-derived structure features.
7. Do not perform large hyperparameter sweeps, threshold sweeps, or indicator fishing.
8. Record failed experiments as carefully as successful ones.
9. Treat 2024 through August 2026 as consumed DEVELOPMENT data, not final untouched validation.
10. Never claim the system is production-ready.

## Frozen execution assumptions

- next-bar-open entry
- 1R take profit
- 1R stop loss
- maximum 15 future bars
- same-bar TP and SL -> conservative stop loss
- 1.00 NQ-point round-trip friction
- 15-minute signal non-overlap

## Frozen model-validation scaffold

- prior 12 months = training
- immediately previous full month = excluded OOS calibration month
- following month = evaluation

## Current major finding

Experiment 23 decomposed the original V2 predictive signal across 32 monthly development windows:

- multiclass macro AUC: 0.5359
- resolution AUC: 0.5771
- conditional direction AUC: 0.5135
- directional accuracy: 51.14%
- resolution AUC exceeded direction AUC in 28 of 32 months

2026 was especially revealing:

- resolution AUC: about 0.600
- direction AUC: about 0.499

The main bottleneck is DIRECTION, not whether price moves enough to resolve.

## Rejected branches

Do not revive these without a genuinely new structural hypothesis:

- confidence-only filtering
- high-volatility filter
- logistic meta-model
- shallow-tree meta-model
- breakeven after +0.50R
- breakeven after +0.75R
- volatility-clock target
- volume-clock target
- binary direction + resolution ranking
- direct long/short expected-R regression
- replacing 12M training with 6M, 18M, or 24M

## First task — Experiment 24

Run the feature-group ablation implemented in `scripts/experiment24.py`.

Feature groups:

MOMENTUM
- ret_1
- ret_3
- ret_5
- body_pct

VOL_SCALE
- range_pct
- volatility_5
- barrier_pct

LOCATION
- vwap_distance
- distance_from_open
- range_position

ACTIVITY_TIME
- volume_ratio_5
- minute_from_open

Configurations:

- ALL_12
- NO_MOMENTUM
- NO_VOL_SCALE
- NO_LOCATION
- NO_ACTIVITY_TIME

Primary metric:
conditional directional AUC on resolved rows.

Secondary metrics:
- resolution AUC
- directional accuracy
- multiclass macro AUC
- year-by-year stability

Experiment 24 is diagnostic only. Do not automatically turn the best-looking configuration into a strategy.

## After Experiment 24

You may design and run at most THREE additional structural experiments aimed specifically at improving causal directional prediction.

Before each experiment, write:

- hypothesis
- exact feature definitions
- causal justification
- falsification criterion
- validation design

Freeze that plan before execution.

Potential research families include:

- multi-horizon signed returns
- normalized displacement
- signed VWAP displacement
- opening-range state
- trend persistence vs. mean reversion
- signed range expansion
- return acceleration/deceleration
- position relative to PRIOR completed-session levels

Do not simply search many indicators or thresholds.

## Required outputs

Maintain `research/EXPERIMENT_LOG.md`.

For every experiment include:

- hypothesis
- exact features
- train/calibration/evaluation scheme
- leakage audit
- sample size
- aggregate results
- yearly results
- conclusion: KEEP / REJECT / INCONCLUSIVE

Save useful tables to `outputs/`.

At the end create `research/OVERNIGHT_REPORT.md` with:

- Experiment 24 results
- every subsequent experiment attempted, including failures
- directional AUC and accuracy by year
- leakage/causality audit
- sample sizes
- what was rejected
- what remains promising
- exact frozen candidate, if any, for genuinely unseen future validation
- explicit post-hoc observations separated from preregistered results
