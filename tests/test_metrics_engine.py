"""Tests for Business Metrics Engine, KPI calculations, and financial semantics."""

import pandas as pd
import pytest

from src.analytics.metrics import compute_all_kpis


def test_compute_all_kpis_comprehensive(synthetic_sales_df):
    """Test full KPI computation suite on mapped synthetic sales data."""
    # Rename columns to standard canonical keys
    canonical_df = synthetic_sales_df.rename(
        columns={
            "Sales": "sales",
            "Profit": "profit",
            "Quantity": "quantity",
            "Discount": "discount",
            "Order ID": "order_id",
            "Customer Name": "customer_name",
        }
    )

    kpi_set = compute_all_kpis(canonical_df, currency_label="USD")

    # Revenue
    assert kpi_set.net_revenue == 2454.90
    assert kpi_set.kpi_dict["net_sales"].is_available

    # Profit
    assert kpi_set.total_profit == 312.60
    assert kpi_set.profit_margin is not None
    assert round(kpi_set.profit_margin, 2) == 12.73

    # Orders & AOV
    assert kpi_set.total_orders == 5
    assert round(kpi_set.aov, 2) == 490.98

    # Customers & Units
    assert kpi_set.kpi_dict["unique_customers"].value == 5
    assert kpi_set.kpi_dict["total_quantity"].value == 13.0


def test_kpi_negative_transactions_returns():
    """Test that negative transactions (returns) are subtracted in net sales and reported accurately."""
    df = pd.DataFrame({
        "sales": [1000.0, 500.0, -200.0],  # Net: 1300, Returns: -200
        "order_id": ["O1", "O2", "O3"],
    })
    kpi_set = compute_all_kpis(df)

    assert kpi_set.net_revenue == 1300.0
    net_kpi = kpi_set.kpi_dict["net_sales"]
    assert "Returns: -$200.00" in net_kpi.sublabel

    # Return rate
    assert kpi_set.kpi_dict["return_rate"].value == pytest.approx(33.33, 0.05)


def test_kpi_zero_revenue_margin_safety():
    """Test that profit margin calculation handles zero revenue safely without raising ZeroDivisionError or NaN."""
    df = pd.DataFrame({
        "sales": [0.0, 0.0],
        "profit": [-50.0, -20.0],
    })
    kpi_set = compute_all_kpis(df)
    margin_kpi = kpi_set.kpi_dict["profit_margin"]

    assert not margin_kpi.is_available
    assert margin_kpi.value is None
    assert margin_kpi.formatted_value == "—"


def test_kpi_missing_order_id_fallback():
    """Test that when order_id is unmapped, rows are counted with an explicit qualification."""
    df = pd.DataFrame({"sales": [100.0, 200.0, 300.0]})
    kpi_set = compute_all_kpis(df)
    orders_kpi = kpi_set.kpi_dict["total_orders"]

    assert orders_kpi.value == 3
    assert "row count" in orders_kpi.sublabel


def test_kpi_indian_numbering_formatting():
    """Test Indian numbering formatting (Lakhs and Crores) for high monetary values."""
    df = pd.DataFrame({
        "sales": [15_000_000.0],  # 1.50 Crore
        "profit": [450_000.0],    # 4.50 Lakh
    })
    kpi_set = compute_all_kpis(df, currency_label="INR", use_indian_numbering=True)

    assert "₹1.50 Cr" in kpi_set.kpi_dict["net_sales"].formatted_value
    assert "₹4.50 L" in kpi_set.kpi_dict["total_profit"].formatted_value
