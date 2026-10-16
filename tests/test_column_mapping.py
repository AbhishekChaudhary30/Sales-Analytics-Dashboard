"""Tests for column alias matching, ambiguity detection, and schema alignment."""

import pandas as pd

from src.data.column_mapping import (
    ColumnMapper,
    auto_detect_mappings,
    create_standard_dataframe,
)
from src.utils.formatting import normalize_column_name


def test_normalize_column_name():
    """Test string cleanup and normalization for column headers."""
    assert normalize_column_name("Order Date") == "order_date"
    assert normalize_column_name("Sales Amount ($)") == "sales_amount"
    assert normalize_column_name("Sub-Category") == "sub_category"
    assert normalize_column_name("  Item  Qty  ") == "item_qty"


def test_auto_detect_mappings():
    """Test auto-mapping candidate detection on standard sales column names."""
    raw_cols = [
        "Order ID",
        "Order Date",
        "Customer Name",
        "Sales",
        "Profit",
        "Discount",
        "Region",
    ]
    result = auto_detect_mappings(raw_cols)

    assert result.detected_mappings["order_id"] == "Order ID"
    assert result.detected_mappings["order_date"] == "Order Date"
    assert result.detected_mappings["customer_name"] == "Customer Name"
    assert result.detected_mappings["sales"] == "Sales"
    assert result.detected_mappings["profit"] == "Profit"
    assert result.confidence_scores["sales"] >= 0.90


def test_column_mapper_overrides():
    """Test manual overrides and essential field verification."""
    raw_cols = ["Trans_Date", "Rev", "Product_Item"]
    mapper = ColumnMapper(raw_cols)

    # Initial state
    mapper.set_mapping("order_date", "Trans_Date")
    mapper.set_mapping("sales", "Rev")

    is_ready, missing = mapper.get_essential_status()
    assert is_ready
    assert len(missing) == 0

    # Unmap sales
    mapper.set_mapping("sales", None)
    is_ready, missing = mapper.get_essential_status()
    assert not is_ready
    assert "Sales / Revenue" in missing


def test_create_standard_dataframe(synthetic_sales_df):
    """Test generating a standardized DataFrame with properly converted datatypes."""
    raw_cols = list(synthetic_sales_df.columns)
    mapper = ColumnMapper(raw_cols)

    std_df = create_standard_dataframe(synthetic_sales_df, mapper.current_mappings)

    assert "sales" in std_df.columns
    assert "order_date" in std_df.columns
    assert pd.api.types.is_numeric_dtype(std_df["sales"])
    assert pd.api.types.is_datetime64_any_dtype(std_df["order_date"])
    assert len(std_df) == len(synthetic_sales_df)


def test_no_false_positive_payment_method_on_superstore():
    """Verify standard Superstore schema without Payment Method does not false-match payment_method."""
    standard_superstore_cols = [
        "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
        "Customer Name", "Segment", "Country", "City", "State", "Postal Code",
        "Region", "Product ID", "Category", "Sub-Category", "Product Name",
        "Sales", "Quantity", "Discount", "Profit"
    ]
    mapper = ColumnMapper(standard_superstore_cols)

    # payment_method must remain None (unmapped)
    assert mapper.current_mappings.get("payment_method") is None
    # shipping_mode must correctly map to Ship Mode
    assert mapper.current_mappings.get("shipping_mode") == "Ship Mode"
    # Unrelated dimensions must not be falsely mapped to payment_method
    assert "Segment" not in [v for k, v in mapper.current_mappings.items() if k == "payment_method"]
    assert "Postal Code" not in [v for k, v in mapper.current_mappings.items() if k == "payment_method"]

