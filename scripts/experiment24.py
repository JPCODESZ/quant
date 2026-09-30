from pathlib import Path
import sys
import numpy as np
import pandas as pd

from pandas.tseries.offsets import DateOffset
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, accuracy_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_data import load_frame, V2_FEATURES


FEATURE_GROUPS = {
    "MOMENTUM": ["ret_1", "ret_3", "ret_5", "body_pct"],
    "VOL_SCALE": ["range_pct", "volatility_5", "barrier_pct"],
    "LOCATION": ["vwap_distance", "distance_from_open", "range_position"],
    "ACTIVITY_TIME": ["volume_ratio_5", "minute_from_open"],
}

CONFIGS = {
    "ALL_12": list(V2_FEATURES),
    "NO_MOMENTUM": [x for x in V2_FEATURES if x not in FEATURE_GROUPS["MOMENTUM"]],
    "NO_VOL_SCALE": [x for x in V2_FEATURES if x not in FEATURE_GROUPS["VOL_SCALE"]],
    "NO_LOCATION": [x for x in V2_FEATURES if x not in FEATURE_GROUPS["LOCATION"]],
    "NO_ACTIVITY_TIME": [x for x in V2_FEATURES if x not in FEATURE_GROUPS["ACTIVITY_TIME"]],
}


def evaluate_config(data, features, target_period):
    target_start = target_period.to_timestamp()
    target_end = target_start + DateOffset(months=1)

    calibration_start = target_start - DateOffset(months=1)
    training_end = calibration_start
    training_start = training_end - DateOffset(months=12)

    train = data[
        (data["ts_date"] >= training_start)
        & (data["ts_date"] < training_end)
    ].copy()

    test = data[
        (data["ts_date"] >= target_start)
        & (data["ts_date"] < target_end)
    ].copy()

    if len(train) == 0 or len(test) == 0:
        return None

    model = HistGradientBoostingClassifier(
        learning_rate=0.04,
        max_iter=250,
        max_leaf_nodes=15,
        min_samples_leaf=150,
        l2_regularization=2.0,
        random_state=42,
    )

    model.fit(train[features], train["target"])
    probs = model.predict_proba(test[features])
    classes = list(model.classes_)

    if not all(c in classes for c in [0, 1, 2]):
        return None

    down_i = classes.index(0)
    up_i = classes.index(1)
    neither_i = classes.index(2)

    p_down = probs[:, down_i]
    p_up = probs[:, up_i]

    try:
        macro_auc = roc_auc_score(
            test["target"],
            probs,
            multi_class="ovr",
            average="macro",
        )
    except Exception:
        macro_auc = np.nan

    true_resolved = test["target"].isin([0, 1]).astype(int).to_numpy()
    p_resolved = p_down + p_up

    try:
        resolution_auc = roc_auc_score(true_resolved, p_resolved)
    except Exception:
        resolution_auc = np.nan

    directional_mask = test["target"].isin([0, 1]).to_numpy()
    directional_test = test.loc[directional_mask]

    denom = p_up[directional_mask] + p_down[directional_mask]
    conditional_p_up = p_up[directional_mask] / np.clip(denom, 1e-12, None)
    true_up = directional_test["target"].eq(1).astype(int).to_numpy()

    try:
        direction_auc = roc_auc_score(true_up, conditional_p_up)
    except Exception:
        direction_auc = np.nan

    predicted_up = (conditional_p_up >= 0.5).astype(int)
    direction_accuracy = accuracy_score(true_up, predicted_up) * 100

    return {
        "month": str(target_period),
        "features": len(features),
        "macro_auc": macro_auc,
        "resolution_auc": resolution_auc,
        "direction_auc": direction_auc,
        "direction_accuracy": direction_accuracy,
    }


def main():
    data = load_frame("model_rows_ext").copy()
    data["ts_date"] = pd.to_datetime(data["date"])

    grouped = [f for g in FEATURE_GROUPS.values() for f in g]
    if set(grouped) != set(V2_FEATURES):
        raise RuntimeError("Feature groups are not an exact partition of V2_FEATURES.")

    months = pd.period_range("2024-01", "2026-08", freq="M")
    records = []

    for config_name, features in CONFIGS.items():
        print(f"Running {config_name} ({len(features)} features)")
        for month in months:
            result = evaluate_config(data, features, month)
            if result is None:
                continue
            result["config"] = config_name
            records.append(result)

    results = pd.DataFrame(records)
    if results.empty:
        raise RuntimeError("Experiment produced no results.")

    aggregate = (
        results.groupby("config")
        .agg(
            months=("month", "size"),
            features=("features", "first"),
            macro_auc=("macro_auc", "mean"),
            resolution_auc=("resolution_auc", "mean"),
            direction_auc=("direction_auc", "mean"),
            direction_accuracy=("direction_accuracy", "mean"),
            direction_months_gt_050=("direction_auc", lambda x: (x > 0.50).sum()),
            resolution_months_gt_050=("resolution_auc", lambda x: (x > 0.50).sum()),
        )
        .reset_index()
    )

    baseline = aggregate[aggregate["config"] == "ALL_12"].iloc[0]
    delta = aggregate.copy()
    delta["delta_macro_auc"] = delta["macro_auc"] - baseline["macro_auc"]
    delta["delta_resolution_auc"] = delta["resolution_auc"] - baseline["resolution_auc"]
    delta["delta_direction_auc"] = delta["direction_auc"] - baseline["direction_auc"]
    delta["delta_direction_accuracy_pp"] = (
        delta["direction_accuracy"] - baseline["direction_accuracy"]
    )

    results["year"] = results["month"].str[:4].astype(int)

    yearly_direction = results.pivot_table(
        index="year", columns="config", values="direction_auc", aggfunc="mean"
    )

    yearly_resolution = results.pivot_table(
        index="year", columns="config", values="resolution_auc", aggfunc="mean"
    )

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    results.to_csv(output_dir / "experiment24_monthly.csv", index=False)
    aggregate.to_csv(output_dir / "experiment24_aggregate.csv", index=False)
    delta.to_csv(output_dir / "experiment24_delta_vs_all12.csv", index=False)
    yearly_direction.to_csv(output_dir / "experiment24_yearly_direction_auc.csv")
    yearly_resolution.to_csv(output_dir / "experiment24_yearly_resolution_auc.csv")

    print("\nEXPERIMENT 24 — AGGREGATE")
    print(
        aggregate.sort_values("direction_auc", ascending=False)
        .round(
            {
                "macro_auc": 4,
                "resolution_auc": 4,
                "direction_auc": 4,
                "direction_accuracy": 2,
            }
        )
        .to_string(index=False)
    )

    print("\nCHANGE VS ALL_12")
    print(
        delta[
            [
                "config",
                "delta_macro_auc",
                "delta_resolution_auc",
                "delta_direction_auc",
                "delta_direction_accuracy_pp",
            ]
        ]
        .sort_values("delta_direction_auc", ascending=False)
        .round(4)
        .to_string(index=False)
    )

    print("\nYEARLY DIRECTION AUC")
    print(yearly_direction.round(4).to_string())

    print("\nYEARLY RESOLUTION AUC")
    print(yearly_resolution.round(4).to_string())


if __name__ == "__main__":
    main()
