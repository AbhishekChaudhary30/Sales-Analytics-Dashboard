"""Tests for Canonical Analytics Data Model and capability checks."""

import pandas as pd

from src.data.canonical import (
    FieldStatus,
    build_canonical_dataset,
    check_capability,
)


def test_build_canonical_dataset_standard():
    """Test standard mapping and normalization of canonical fields."""
    raw_df = pd.DataFrame({
        "Trans_Date": ["2023-01-10", "2023-02-15"],
        "Revenue": [1500.0, 2400.0],
        "Qty": [3, 4],
        "Extra_Col": ["A", "B"],
    })
    mappings = {
        "order_date": "Trans_Date",
        "sales": "Revenue",
        "quantity": "Qty",
    }

    canon = build_canonical_dataset(raw_df, mappings)
    assert canon.field_status["sales"] == FieldStatus.AVAILABLE
    assert canon.field_status["order_date"] == FieldStatus.AVAILABLE
    assert canon.field_status["quantity"] == FieldStatus.AVAILABLE
    assert canon.field_status["profit"] == FieldStatus.UNAVAILABLE
    assert "unmapped_Extra_Col" in canon.df.columns
    assert len(canon.df) == 2


def test_derive_revenue_from_qty_and_price():
    """Test deriving sales from quantity * unit_price when sales is not mapped."""
    raw_df = pd.DataFrame({
        "Units": [2, 5],
        "Price": [10.0, 20.0],
    })
    mappings = {
        "quantity": "Units",
        "unit_price": "Price",
    }

    canon = build_canonical_dataset(raw_df, mappings, allow_derived_revenue=True)
    assert canon.field_status["sales"] == FieldStatus.DERIVED
    assert list(canon.df["sales"]) == [20.0, 100.0]


def test_derive_profit_from_sales_and_cost():
    """Test deriving profit from sales - cost when profit is not mapped."""
    raw_df = pd.DataFrame({
        "Sales": [100.0, 200.0],
        "Cost": [70.0, 150.0],
    })
    mappings = {
        "sales": "Sales",
        "cost": "Cost",
    }

    canon = build_canonical_dataset(raw_df, mappings, allow_derived_profit=True)
    assert canon.field_status["profit"] == FieldStatus.DERIVED
    assert list(canon.df["profit"]) == [30.0, 50.0]


def test_check_capability():
    """Test verifying required analytical fields and generating actionable explanations."""
    raw_df = pd.DataFrame({"sales": [100.0, 200.0]})
    canon = build_canonical_dataset(raw_df, {"sales": "sales"})

    status_ok = check_capability(canon, ["sales"], "Revenue Overview")
    assert status_ok.can_execute
    assert len(status_ok.missing_fields) == 0

    status_fail = check_capability(canon, ["sales", "order_date"], "Time Series Trends")
    assert not status_fail.can_execute
    assert "order_date" in status_fail.missing_fields
    assert "Time Series Trends requires:" in status_fail.explanation
