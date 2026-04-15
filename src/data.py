"""
NYC 311 data — direct Socrata API fetch, no database required.
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

SOCRATA_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
PAGE_SIZE   = 50_000
MAX_PAGES   = 4       # up to 200 K records — covers 90 days comfortably

FIELDS = [
    "unique_key", "created_date", "closed_date", "agency",
    "complaint_type", "descriptor", "status", "borough",
    "incident_zip", "latitude", "longitude",
]


def fetch_raw(days: int = 30) -> pd.DataFrame:
    """
    Fetch recent NYC 311 records directly from the Socrata public API.
    Returns a cleaned, analysis-ready DataFrame.
    No API key or database required.
    """
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00")
    all_rows: list = []

    for page in range(MAX_PAGES):
        params = {
            "$select": ",".join(FIELDS),
            "$where": f"created_date >= '{start}'",
            "$limit": PAGE_SIZE,
            "$offset": page * PAGE_SIZE,
            "$order": "created_date ASC",
        }
        resp = requests.get(SOCRATA_URL, params=params, timeout=60)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        all_rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break  # reached the last page

    if not all_rows:
        empty_cols = FIELDS + ["resolution_hours", "month"]
        return pd.DataFrame(columns=empty_cols)

    df = pd.DataFrame(all_rows)

    # Ensure all expected columns exist
    for col in FIELDS:
        if col not in df.columns:
            df[col] = None

    # ── Type coercions ───────────────────────────────────────────────────────
    df["created_date"]   = pd.to_datetime(df["created_date"],  errors="coerce")
    df["closed_date"]    = pd.to_datetime(df["closed_date"],   errors="coerce")
    df["latitude"]       = pd.to_numeric(df["latitude"],       errors="coerce")
    df["longitude"]      = pd.to_numeric(df["longitude"],      errors="coerce")
    df["borough"]        = (df["borough"].fillna("UNSPECIFIED")
                              .str.upper().str.strip())
    df["agency"]         = (df["agency"].fillna("UNKNOWN")
                              .str.strip())
    df["complaint_type"] = (df["complaint_type"].fillna("UNKNOWN")
                              .str.strip())
    df["status"]         = (df["status"].fillna("")
                              .str.upper().str.strip())

    df = df.dropna(subset=["created_date"])

    # Resolution hours (closed tickets only; clamp negatives)
    df["resolution_hours"] = np.where(
        df["closed_date"].notna(),
        (df["closed_date"] - df["created_date"]).dt.total_seconds() / 3600,
        np.nan,
    )
    df["resolution_hours"] = df["resolution_hours"].where(
        df["resolution_hours"] >= 0
    )

    # Month bucket for time-series grouping
    df["month"] = df["created_date"].dt.to_period("M").dt.to_timestamp()

    return df.reset_index(drop=True)


# ── Mart-style aggregation helpers ───────────────────────────────────────────

def kpi_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly KPIs matching the old marts.kpi_monthly schema."""
    out = (
        df.groupby("month", sort=True)
        .agg(
            total_requests=("unique_key", "count"),
            open_requests=("closed_date", lambda s: s.isna().sum()),
            closed_requests=("closed_date", lambda s: s.notna().sum()),
            median_resolution_hours=(
                "resolution_hours",
                lambda s: float(np.nanmedian(s)) if s.notna().any() else np.nan,
            ),
            p90_resolution_hours=(
                "resolution_hours",
                lambda s: float(np.nanpercentile(s.dropna(), 90))
                          if s.notna().any() else np.nan,
            ),
        )
        .reset_index()
    )
    return out


def top_complaints_monthly(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top-N complaint types per (month, borough)."""
    grp = (
        df.groupby(["month", "borough", "complaint_type"])
        .size()
        .reset_index(name="requests")
    )
    grp["_rank"] = grp.groupby(["month", "borough"])["requests"].rank(
        method="first", ascending=False
    )
    return (
        grp[grp["_rank"] <= top_n]
        .drop(columns="_rank")
        .sort_values(["month", "borough", "requests"],
                     ascending=[True, True, False])
        .reset_index(drop=True)
    )


def agency_performance_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly agency performance metrics."""
    out = (
        df.groupby(["month", "agency"], sort=True)
        .agg(
            requests=("unique_key", "count"),
            median_resolution_hours=(
                "resolution_hours",
                lambda s: float(np.nanmedian(s)) if s.notna().any() else np.nan,
            ),
            p90_resolution_hours=(
                "resolution_hours",
                lambda s: float(np.nanpercentile(s.dropna(), 90))
                          if s.notna().any() else np.nan,
            ),
        )
        .reset_index()
    )
    return out
