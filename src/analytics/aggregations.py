"""Aggregation utilities for time series, category grouping, and dimensional rollups."""

import pandas as pd


def aggregate_by_time(
    df: pd.DataFrame,
    date_col: str = "order_date",
    metric_col: str = "sales",
    freq: str = "ME",  # Monthly frequency (pandas 2.2+ standard)
) -> pd.DataFrame:
    """Aggregate a financial metric over time intervals (Monthly, Weekly, Quarterly)."""
    if df.empty or date_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[date_col, metric_col]).copy()
    valid_df[date_col] = pd.to_datetime(valid_df[date_col], errors="coerce")
    valid_df[metric_col] = pd.to_numeric(valid_df[metric_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[date_col, metric_col])

    if valid_df.empty:
        return pd.DataFrame()

    try:
        # Group by specified period
        grouped = (
            valid_df.set_index(date_col)
            .resample(freq)[metric_col]
            .sum()
            .reset_index()
        )
        grouped.columns = [date_col, metric_col]
        return grouped
    except Exception:
        # Fallback if resample freq is unsupported
        grouped = (
            valid_df.groupby(valid_df[date_col].dt.to_period("M"))[metric_col]
            .sum()
            .reset_index()
        )
        grouped[date_col] = grouped[date_col].dt.to_timestamp()
        return grouped


def aggregate_by_category(
    df: pd.DataFrame,
    cat_col: str = "category",
    metric_col: str = "sales",
    top_n: int = 10,
) -> pd.DataFrame:
    """Aggregate metrics by category or product grouping, sorted descending."""
    if df.empty or cat_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[cat_col, metric_col]).copy()
    valid_df[metric_col] = pd.to_numeric(valid_df[metric_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[metric_col])

    if valid_df.empty:
        return pd.DataFrame()

    grouped = (
        valid_df.groupby(cat_col)[metric_col]
        .sum()
        .reset_index()
        .sort_values(by=metric_col, ascending=False)
        .head(top_n)
    )
    return grouped


def aggregate_by_dimension(
    df: pd.DataFrame,
    dim_col: str,
    metrics: list[str],
) -> pd.DataFrame:
    """Aggregate multiple metrics for any dimensional column (e.g. Region, State)."""
    valid_metrics = [m for m in metrics if m in df.columns]
    if df.empty or dim_col not in df.columns or not valid_metrics:
        return pd.DataFrame()

    agg_dict = {m: "sum" for m in valid_metrics}
    grouped = df.groupby(dim_col).agg(agg_dict).reset_index()
    return grouped
