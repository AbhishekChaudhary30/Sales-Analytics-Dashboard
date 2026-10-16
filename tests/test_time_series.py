"""Tests for Time Series Aggregations, Moving Averages, and Period Comparisons."""

import pandas as pd

from src.analytics.time_series import (
    aggregate_time_series,
    calculate_year_over_year,
    compare_periods,
    parse_and_validate_dates,
)


def test_parse_and_validate_dates():
    """Test date parsing with valid and invalid mixed records."""
    df = pd.DataFrame({
        "order_date": ["2023-01-15", "invalid_date", "2023-03-20", None],
        "sales": [100.0, 200.0, 300.0, 400.0],
    })
    clean_df, telemetry = parse_and_validate_dates(df, date_col="order_date")

    assert len(clean_df) == 2
    assert telemetry["valid_dates"] == 2
    assert telemetry["invalid_dates"] == 2
    assert telemetry["min_date"] == "2023-01-15"
    assert telemetry["max_date"] == "2023-03-20"


def test_aggregate_time_series_monthly():
    """Test monthly aggregation and rolling moving average."""
    df = pd.DataFrame({
        "order_date": pd.date_range("2023-01-01", periods=90, freq="D"),
        "sales": [10.0] * 90,
    })
    res = aggregate_time_series(df, date_col="order_date", metric_col="sales", freq="ME", moving_avg_window=3)

    assert len(res) == 3  # Jan, Feb, Mar
    assert res["sales"].iloc[0] == 310.0  # Jan has 31 days
    assert "sales_ma3" in res.columns


def test_compare_periods_growth_and_decline():
    """Test Period-over-Period (PoP) comparison with positive growth."""
    df = pd.DataFrame({
        "order_date": ["2023-01-15", "2023-02-15"],
        "sales": [1000.0, 1500.0],
    })
    pop = compare_periods(df, date_col="order_date", metric_col="sales", freq="ME")

    assert pop is not None
    assert pop.current_value == 1500.0
    assert pop.previous_value == 1000.0
    assert pop.absolute_change == 500.0
    assert pop.percentage_change == 50.0
    assert pop.is_growth is True


def test_compare_periods_previous_zero_safety():
    """Test that zero in the baseline period prevents ZeroDivisionError and sets percentage_change to None."""
    df = pd.DataFrame({
        "order_date": ["2023-01-15", "2023-02-15"],
        "sales": [0.0, 500.0],
    })
    pop = compare_periods(df, date_col="order_date", metric_col="sales", freq="ME")

    assert pop is not None
    assert pop.is_previous_zero is True
    assert pop.percentage_change is None
    assert pop.absolute_change == 500.0


def test_calculate_year_over_year():
    """Test pivoting monthly totals across years for YoY inspection."""
    df = pd.DataFrame({
        "order_date": ["2023-01-15", "2024-01-15", "2023-02-10", "2024-02-10"],
        "sales": [100.0, 150.0, 200.0, 260.0],
    })
    yoy_df = calculate_year_over_year(df, date_col="order_date", metric_col="sales")

    assert not yoy_df.empty
    assert 2023 in yoy_df.columns
    assert 2024 in yoy_df.columns
    assert len(yoy_df) == 2  # Jan and Feb
