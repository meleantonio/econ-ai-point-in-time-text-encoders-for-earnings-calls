from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

DATA_SOURCE_NAME = "identifiers/calls.csv.gz from Alessiobrini/point-in-time-encoders-for-earnings-calls"
DATA_SOURCE_URL = "https://raw.githubusercontent.com/Alessiobrini/point-in-time-encoders-for-earnings-calls/main/identifiers/calls.csv.gz"
CUTOFF = pd.Timestamp("2019-12-31")


def load_identifiers(url: str = DATA_SOURCE_URL) -> pd.DataFrame:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return pd.read_csv(BytesIO(response.content), compression="gzip")


def _parse_candidate(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    return parsed.dt.tz_convert(None)


def infer_date_column(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    scored = []
    for col in cols:
        name = str(col).lower()
        if any(token in name for token in ["date", "time", "datetime", "timestamp", "call", "transcript", "published", "release"]):
            parsed = _parse_candidate(df[col])
            rate = parsed.notna().mean()
            if rate > 0.05:
                span = parsed.max() - parsed.min() if parsed.notna().any() else pd.Timedelta(0)
                scored.append((rate, span, col))
    if scored:
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return scored[0][2]

    # Fallback: try every non-numeric column and pick the one with the best parse rate.
    fallback = []
    for col in cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        parsed = _parse_candidate(df[col])
        rate = parsed.notna().mean()
        if rate > 0.05:
            span = parsed.max() - parsed.min() if parsed.notna().any() else pd.Timedelta(0)
            fallback.append((rate, span, col))
    if not fallback:
        raise ValueError(f"Could not infer a date column from headers: {cols}")
    fallback.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return fallback[0][2]


def count_cutoff(df: pd.DataFrame, date_col: str, cutoff: pd.Timestamp) -> tuple[int, int]:
    parsed = _parse_candidate(df[date_col])
    cutoff_count = int((parsed <= cutoff).sum())
    full_count = int(len(df))
    return full_count, cutoff_count


def main() -> None:
    df = load_identifiers()
    date_col = infer_date_column(df)
    full_count, cutoff_count = count_cutoff(df, date_col, CUTOFF)
    gap = full_count - cutoff_count

    print("Point-in-time earnings-call audit")
    print(f"Data source: {DATA_SOURCE_URL}")
    print(f"Rows in archive: {full_count}")
    print(f"Inferred date column: {date_col}")
    print(f"Cutoff: {CUTOFF.date().isoformat()}")
    print(f"Rows available by cutoff: {cutoff_count}")
    print(f"Future rows excluded: {gap}")

    if cutoff_count >= full_count:
        raise RuntimeError("Cutoff filtering failed: no rows were excluded.")
    if gap <= 0:
        raise RuntimeError("Expected the full archive to exceed the cutoff sample.")

    print("Wrong-number check passed: the full archive is not the historical sample.")


if __name__ == "__main__":
    main()
