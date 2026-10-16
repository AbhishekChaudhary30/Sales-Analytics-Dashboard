"""Tests for Statistical Distributions, Correlation Heatmaps, and IQR Outliers."""

import pandas as pd

from src.analytics.statistics import (
    compute_correlation_matrix,
    compute_descriptive_stats,
    detect_iqr_outliers,
)


def test_compute_descriptive_stats():
    """Test generating distribution statistics including quartiles, IQR, and skewness."""
    df = pd.DataFrame({
        "sales": [10.0, 20.0, 30.0, 40.0, 50.0],
        "profit": [2.0, 4.0, 6.0, 8.0, 10.0],
    })
    stats_df = compute_descriptive_stats(df)

    assert len(stats_df) == 2
    sales_stat = stats_df[stats_df["Metric"] == "Sales"].iloc[0]
    assert sales_stat["Mean"] == 30.0
    assert sales_stat["Median (50%)"] == 30.0
    assert sales_stat["Min"] == 10.0
    assert sales_stat["Max"] == 50.0


def test_compute_correlation_matrix():
    """Test calculating Pearson and Spearman correlation matrices across measures."""
    df = pd.DataFrame({
        "sales": [100.0, 200.0, 300.0, 400.0],
        "profit": [20.0, 40.0, 60.0, 80.0],  # Perfect positive correlation
        "discount": [0.4, 0.3, 0.2, 0.1],   # Negative correlation
    })
    corr = compute_correlation_matrix(df, method="pearson")

    assert not corr.empty
    assert corr.loc["sales", "profit"] == 1.0
    assert corr.loc["sales", "discount"] == -1.0


def test_detect_iqr_outliers():
    """Test detecting extreme statistical anomalies via the Interquartile Range method."""
    # Data with a clear extreme outlier (9999.0)
    sales = [10.0, 12.0, 11.0, 14.0, 15.0, 13.0, 12.0, 16.0, 9999.0]
    df = pd.DataFrame({"sales": sales})

    outlier_res = detect_iqr_outliers(df, column_name="sales", multiplier=1.5)
    assert outlier_res is not None
    assert outlier_res.outlier_count == 1
    assert outlier_res.outlier_rows.iloc[0]["sales"] == 9999.0
