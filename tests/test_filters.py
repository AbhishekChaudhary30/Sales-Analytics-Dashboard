"""Tests for Dynamic Multi-Dimensional Filtering Engine."""

from datetime import date

import pandas as pd

from src.analytics.filters import FilterState, apply_filters


def test_apply_filters_categories_and_regions():
    """Test multi-dimensional filtering across categories and regions."""
    df = pd.DataFrame({
        "category": ["Tech", "Office", "Furniture", "Tech"],
        "region": ["East", "West", "East", "West"],
        "sales": [100.0, 200.0, 300.0, 400.0],
    })

    filters = FilterState(categories=["Tech"], regions=["East"])
    res = apply_filters(df, filters)

    assert res.total_original == 4
    assert res.total_remaining == 1
    assert res.filtered_df.iloc[0]["sales"] == 100.0
    assert not res.is_empty


def test_apply_filters_date_range():
    """Test date interval boundary filtering."""
    df = pd.DataFrame({
        "order_date": ["2023-01-10", "2023-02-15", "2023-03-20"],
        "sales": [100.0, 200.0, 300.0],
    })

    filters = FilterState(date_range=(date(2023, 1, 1), date(2023, 2, 28)))
    res = apply_filters(df, filters)

    assert res.total_remaining == 2
    assert "2023-03-20" not in list(res.filtered_df["order_date"].astype(str))


def test_apply_filters_transaction_type_returns():
    """Test filtering strictly for negative transactions (returns)."""
    df = pd.DataFrame({
        "sales": [500.0, -100.0, 200.0, -50.0],
    })
    filters = FilterState(transaction_type="Returns / Refunds Only")
    res = apply_filters(df, filters)

    assert res.total_remaining == 2
    assert (res.filtered_df["sales"] < 0).all()


def test_apply_filters_empty_result():
    """Test that mutually exclusive filters produce a safe empty result with is_empty=True."""
    df = pd.DataFrame({
        "category": ["Tech", "Office"],
        "sales": [100.0, 200.0],
    })
    filters = FilterState(categories=["NonExistentCategory"])
    res = apply_filters(df, filters)

    assert res.total_remaining == 0
    assert res.is_empty is True
