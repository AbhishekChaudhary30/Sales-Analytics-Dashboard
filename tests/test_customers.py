"""Tests for Customer Intelligence, Concentration, and Repeat Retention Analytics."""

import pandas as pd
import pytest

from src.analytics.customers import (
    analyze_customer_concentration,
    analyze_repeat_customers,
    rank_customers,
)


def test_rank_customers():
    """Test ranking customers by total revenue contribution."""
    df = pd.DataFrame({
        "customer_name": ["Alice", "Bob", "Alice", "Charlie"],
        "sales": [500.0, 300.0, 700.0, 100.0],
        "profit": [100.0, 50.0, 150.0, 20.0],
        "order_id": ["O1", "O2", "O3", "O4"],
    })
    ranked = rank_customers(df, cust_col="customer_name", top_n=2)

    assert len(ranked) == 2
    assert ranked.iloc[0]["customer_name"] == "Alice"
    assert ranked.iloc[0]["sales"] == 1200.0
    assert ranked.iloc[0]["orders_count"] == 2


def test_analyze_customer_concentration():
    """Test evaluating customer concentration metrics among top accounts."""
    df = pd.DataFrame({
        "customer_name": [f"Client_{i}" for i in range(10)],
        "sales": [500.0, 300.0, 200.0, 100.0, 100.0, 50.0, 50.0, 50.0, 25.0, 25.0],
    })
    conc = analyze_customer_concentration(df, cust_col="customer_name", sales_col="sales")

    assert conc is not None
    assert conc.total_customers == 10
    assert conc.total_revenue == 1400.0
    assert conc.top5_revenue == 1200.0
    assert conc.top5_share_pct == pytest.approx(85.71, 0.05)
    assert conc.concentration_level == "High"


def test_analyze_repeat_customers():
    """Test repeat buyer rates and repeat revenue share."""
    df = pd.DataFrame({
        "customer_name": ["Alice", "Alice", "Bob", "Charlie"],
        "order_id": ["O1", "O2", "O3", "O4"],
        "sales": [100.0, 150.0, 80.0, 90.0],
    })
    rep = analyze_repeat_customers(df, cust_col="customer_name", order_col="order_id", sales_col="sales")

    assert rep is not None
    assert rep.total_customers == 3
    assert rep.repeat_customers == 1  # Alice
    assert rep.single_order_customers == 2  # Bob & Charlie
    assert rep.repeat_rate_pct == pytest.approx(33.33, 0.05)
    assert rep.repeat_revenue == 250.0
