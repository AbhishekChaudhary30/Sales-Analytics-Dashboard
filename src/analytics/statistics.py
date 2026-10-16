"""Statistical Distributions, Correlation Matrices, and Outlier Analysis."""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd


@dataclass
class OutlierSummary:
    """Summary of statistical anomalies detected via the Interquartile Range (IQR) method."""

    column_name: str
    lower_bound: float
    upper_bound: float
    outlier_count: int
    outlier_percentage: float
    outlier_rows: pd.DataFrame


def compute_descriptive_stats(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """Calculate comprehensive distribution metrics for numeric measures."""
    if df.empty:
        return pd.DataFrame()

    if numeric_cols is None:
        target_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    else:
        target_cols = [c for c in numeric_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]

    if not target_cols:
        return pd.DataFrame()

    stats_list = []
    for col in target_cols:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue

        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25

        stats_list.append({
            "Metric": col.replace("_", " ").title(),
            "Non-Null Count": len(series),
            "Mean": round(float(series.mean()), 2),
            "Std Dev": round(float(series.std()), 2) if len(series) > 1 else 0.0,
            "Min": round(float(series.min()), 2),
            "Q25 (25%)": round(q25, 2),
            "Median (50%)": round(float(series.median()), 2),
            "Q75 (75%)": round(q75, 2),
            "Max": round(float(series.max()), 2),
            "IQR": round(iqr, 2),
            "Skewness": round(float(series.skew()), 2) if len(series) > 2 else 0.0,
        })

    return pd.DataFrame(stats_list)


def compute_correlation_matrix(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """Compute Pearson or Spearman correlation matrix across numeric measures."""
    if df.empty:
        return pd.DataFrame()

    if columns is None:
        num_df = df.select_dtypes(include=[np.number])
    else:
        valid_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        num_df = df[valid_cols]

    # Exclude columns with zero variance (constant values)
    active_cols = [col for col in num_df.columns if num_df[col].nunique() > 1]
    if len(active_cols) < 2:
        return pd.DataFrame()

    corr_df = num_df[active_cols].corr(method=method).round(2)
    return corr_df


def detect_iqr_outliers(
    df: pd.DataFrame,
    column_name: str = "sales",
    multiplier: float = 1.5,
) -> Optional[OutlierSummary]:
    """Detect statistical outliers using the non-parametric Interquartile Range method."""
    if df.empty or column_name not in df.columns or not pd.api.types.is_numeric_dtype(df[column_name]):
        return None

    series = pd.to_numeric(df[column_name], errors="coerce").dropna()
    if len(series) < 5:
        return None

    q25 = float(series.quantile(0.25))
    q75 = float(series.quantile(0.75))
    iqr = q75 - q25

    if iqr == 0:
        return None

    lower_bound = q25 - (multiplier * iqr)
    upper_bound = q75 + (multiplier * iqr)

    outlier_mask = (df[column_name] < lower_bound) | (df[column_name] > upper_bound)
    outlier_df = df[outlier_mask]
    outlier_count = len(outlier_df)
    total_valid = len(series)
    outlier_pct = round((outlier_count / total_valid * 100.0), 2) if total_valid > 0 else 0.0

    return OutlierSummary(
        column_name=column_name,
        lower_bound=round(lower_bound, 2),
        upper_bound=round(upper_bound, 2),
        outlier_count=outlier_count,
        outlier_percentage=outlier_pct,
        outlier_rows=outlier_df,
    )
