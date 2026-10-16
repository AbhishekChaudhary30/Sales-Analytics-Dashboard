"""Tests for Profitability, Loss-Making Transactions, and Discount Tier Segmentation."""

import pandas as pd
import pytest

from src.analytics.profitability import (
    analyze_discount_tiers,
    analyze_loss_making_transactions,
)


def test_analyze_loss_making_transactions():
    """Test identifying negative-profit orders and total loss sums."""
    df = pd.DataFrame({
        "product_name": ["Widget A", "Widget B", "Widget C"],
        "category": ["Tech", "Office", "Office"],
        "sales": [100.0, 50.0, 80.0],
        "profit": [25.0, -20.0, -15.0],
    })
    loss = analyze_loss_making_transactions(df)

    assert loss is not None
    assert loss.total_loss_transactions == 2
    assert loss.total_loss_amount == 35.0
    assert loss.loss_transaction_rate_pct == pytest.approx(66.67, 0.05)
    assert len(loss.top_loss_products) == 2


def test_analyze_discount_tiers():
    """Test segmenting transactions into standard discount bands and computing margin differences."""
    df = pd.DataFrame({
        "discount": [0.0, 0.05, 0.15, 0.30],
        "sales": [100.0, 100.0, 100.0, 100.0],
        "profit": [30.0, 20.0, 10.0, -10.0],
    })
    disc_summary = analyze_discount_tiers(df)

    assert disc_summary is not None
    assert not disc_summary.tier_df.empty
    assert disc_summary.no_discount_margin_pct == 30.0
    assert disc_summary.high_discount_margin_pct == -10.0
    assert disc_summary.correlation_discount_profit is not None
    assert disc_summary.correlation_discount_profit < 0  # Discount negatively correlates with profit
