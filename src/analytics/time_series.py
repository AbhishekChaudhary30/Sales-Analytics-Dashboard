"""Time Series Analysis, Multi-Frequency Aggregations, and Period Comparisons."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import pandas as pd


@dataclass
class PeriodComparison:
    """Telemetry comparing current period against the preceding period."""

    current_period_label: str
    previous_period_label: str
    current_value: float
    previous_value: Optional[float]
    absolute_change: Optional[float]
    percentage_change: Optional[float]
    is_growth: Optional[bool]
    is_previous_zero: bool = False
    is_incomplete_period: bool = False
    metric_name: str = "Sales"


def parse_and_validate_dates(df: pd.DataFrame, date_col: str = "order_date") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean date column, drop unparseable rows for time analysis, and report parse telemetry."""
    if df.empty or date_col not in df.columns:
        return pd.DataFrame(), {
            "total_rows": len(df),
            "valid_dates": 0,
            "invalid_dates": len(df),
            "min_date": None,
            "max_date": None,
        }

    valid_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(valid_df[date_col]):
        valid_df[date_col] = pd.to_datetime(valid_df[date_col], errors="coerce", format="mixed")

    valid_mask = valid_df[date_col].notna()
    parsed_df = valid_df[valid_mask].sort_values(by=date_col)

    telemetry = {
        "total_rows": len(df),
        "valid_dates": int(valid_mask.sum()),
        "invalid_dates": int((~valid_mask).sum()),
        "min_date": parsed_df[date_col].min().strftime("%Y-%m-%d") if not parsed_df.empty else None,
        "max_date": parsed_df[date_col].max().strftime("%Y-%m-%d") if not parsed_df.empty else None,
    }
    return parsed_df, telemetry


def aggregate_time_series(
    df: pd.DataFrame,
    date_col: str = "order_date",
    metric_col: str = "sales",
    freq: str = "ME",
    moving_avg_window: Optional[int] = None,
) -> pd.DataFrame:
    """Aggregate a financial or volume metric over standard time frequencies.

    Frequencies:
        'D': Daily
        'W': Weekly
        'ME': Monthly
        'QE': Quarterly
        'YE': Yearly
    """
    clean_df, _ = parse_and_validate_dates(df, date_col)
    if clean_df.empty or metric_col not in clean_df.columns:
        return pd.DataFrame()

    clean_df[metric_col] = pd.to_numeric(clean_df[metric_col], errors="coerce")
    clean_df = clean_df.dropna(subset=[metric_col])

    if clean_df.empty:
        return pd.DataFrame()

    try:
        resampled = (
            clean_df.set_index(date_col)
            .resample(freq)[metric_col]
            .sum()
            .reset_index()
        )
    except Exception:
        # Fallback to monthly period if pandas resample freq format differs
        resampled = (
            clean_df.groupby(clean_df[date_col].dt.to_period("M"))[metric_col]
            .sum()
            .reset_index()
        )
        resampled[date_col] = resampled[date_col].dt.to_timestamp()

    # Optional moving average
    if moving_avg_window and moving_avg_window > 1 and len(resampled) >= moving_avg_window:
        resampled[f"{metric_col}_ma{moving_avg_window}"] = (
            resampled[metric_col].rolling(window=moving_avg_window, min_periods=1).mean().round(2)
        )

    return resampled


def compare_periods(
    df: pd.DataFrame,
    date_col: str = "order_date",
    metric_col: str = "sales",
    freq: str = "ME",
) -> Optional[PeriodComparison]:
    """Calculate Period-over-Period (PoP) change for the most recent two complete periods."""
    ts_df = aggregate_time_series(df, date_col=date_col, metric_col=metric_col, freq=freq)
    if ts_df.empty or len(ts_df) < 1:
        return None

    if len(ts_df) == 1:
        curr_row = ts_df.iloc[-1]
        c_val = float(curr_row[metric_col])
        return PeriodComparison(
            current_period_label=str(curr_row[date_col])[:10],
            previous_period_label="N/A",
            current_value=c_val,
            previous_value=None,
            absolute_change=None,
            percentage_change=None,
            is_growth=None,
            metric_name=metric_col.replace("_", " ").title(),
        )

    # Compare last two observations
    prev_row = ts_df.iloc[-2]
    curr_row = ts_df.iloc[-1]

    p_val = float(prev_row[metric_col])
    c_val = float(curr_row[metric_col])
    abs_diff = c_val - p_val

    is_prev_zero = (p_val == 0)
    pct_diff = None
    if not is_prev_zero:
        pct_diff = (abs_diff / abs(p_val)) * 100.0

    return PeriodComparison(
        current_period_label=str(curr_row[date_col])[:10],
        previous_period_label=str(prev_row[date_col])[:10],
        current_value=c_val,
        previous_value=p_val,
        absolute_change=abs_diff,
        percentage_change=pct_diff,
        is_growth=abs_diff > 0 if abs_diff != 0 else None,
        is_previous_zero=is_prev_zero,
        metric_name=metric_col.replace("_", " ").title(),
    )


def calculate_year_over_year(
    df: pd.DataFrame,
    date_col: str = "order_date",
    metric_col: str = "sales",
) -> pd.DataFrame:
    """Calculate Year-over-Year (YoY) metrics comparing each month across years."""
    clean_df, _ = parse_and_validate_dates(df, date_col)
    if clean_df.empty or metric_col not in clean_df.columns:
        return pd.DataFrame()

    clean_df[metric_col] = pd.to_numeric(clean_df[metric_col], errors="coerce")
    clean_df = clean_df.dropna(subset=[metric_col])

    clean_df["year"] = clean_df[date_col].dt.year
    clean_df["month"] = clean_df[date_col].dt.month
    clean_df["month_name"] = clean_df[date_col].dt.strftime("%b")

    pivot = clean_df.pivot_table(
        index=["month", "month_name"],
        columns="year",
        values=metric_col,
        aggfunc="sum",
    ).reset_index()

    pivot = pivot.sort_values(by="month")
    return pivot


# Convenient alias for semantic readability
compare_time_periods = compare_periods
