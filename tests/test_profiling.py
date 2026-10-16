"""Tests for dataset profiling, statistical summaries, and quality warnings."""

import pandas as pd

from src.data.profiling import infer_column_semantic_type, profile_dataset


def test_infer_column_semantic_type():
    """Test heuristic semantic type inference for various column types."""
    # Datetime series
    date_series = pd.Series(["2023-01-01", "2023-01-02", "2023-01-03"])
    sem_type, _ = infer_column_semantic_type(date_series, "order_date")
    assert sem_type == "datetime"

    # Numeric series formatted as currency strings
    curr_series = pd.Series(["$100.50", "$250.00", "$90.00"])
    sem_type, _ = infer_column_semantic_type(curr_series, "sales_amount")
    assert sem_type == "numeric"

    # ID series
    id_series = pd.Series(["ORD-001", "ORD-002", "ORD-003"])
    sem_type, _ = infer_column_semantic_type(id_series, "order_id")
    assert sem_type == "id"

    # Categorical series
    cat_series = pd.Series(["East", "West", "East", "West", "East"])
    sem_type, _ = infer_column_semantic_type(cat_series, "region")
    assert sem_type == "categorical"


def test_profile_dataset(synthetic_sales_df):
    """Test generating a complete profile for synthetic sales data."""
    profile = profile_dataset(synthetic_sales_df)

    assert profile.total_rows == 5
    assert profile.total_cols == 10
    assert profile.duplicate_rows_count == 0
    assert "Sales" in profile.candidate_numeric_cols
    assert "Order Date" in profile.candidate_datetime_cols

    # Check numeric statistics on Sales column
    sales_profile = profile.columns_profile["Sales"]
    assert sales_profile.num_min == 34.50
    assert sales_profile.num_max == 1200.50
    assert sales_profile.num_mean > 0


def test_profile_quality_warnings():
    """Test that high missing values and duplicate rows trigger quality warnings."""
    df = pd.DataFrame({
        "ID": [1, 1, 1, 1],
        "HighMissing": [None, None, None, 10.0],
        "Constant": ["A", "A", "A", "A"],
    })
    profile = profile_dataset(df)

    assert profile.duplicate_rows_count >= 1
    assert any("missing values" in w.lower() for w in profile.quality_warnings)
    assert any("duplicate rows" in w.lower() for w in profile.quality_warnings)
