from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

V2_FEATURES = [
    "minute_from_open",
    "ret_1",
    "ret_3",
    "ret_5",
    "range_pct",
    "body_pct",
    "volatility_5",
    "volume_ratio_5",
    "vwap_distance",
    "distance_from_open",
    "range_position",
    "barrier_pct",
]

EXPECTED_ROWS = {
    "v2_ext": 108270,
    "model_rows_ext": 79148,
    "audit20": 108270,
    "wf26_trades": 372,
}


def load_frame(name: str) -> pd.DataFrame:
    path = ROOT / "data" / f"{name}.csv.gz"
    df = pd.read_csv(path)

    if "_row_index" in df.columns:
        df = df.set_index("_row_index")
        try:
            df.index = df.index.astype(int)
        except Exception:
            pass

    for col in ("timestamp", "ts_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def verify_bundle():
    loaded = {}
    for name, expected in EXPECTED_ROWS.items():
        frame = load_frame(name)
        loaded[name] = frame
        if len(frame) != expected:
            raise ValueError(
                f"{name}: expected {expected:,} rows, got {len(frame):,}"
            )

    missing = [f for f in V2_FEATURES if f not in loaded["model_rows_ext"].columns]
    if missing:
        raise ValueError(f"model_rows_ext missing frozen features: {missing}")

    return loaded


if __name__ == "__main__":
    frames = verify_bundle()
    for name, frame in frames.items():
        print(f"{name}: {len(frame):,} rows")
    print("Frozen feature count:", len(V2_FEATURES))
    print("Bundle verification passed.")
