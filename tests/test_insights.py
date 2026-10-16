"""Tests for Evidence-Based Automated Insights Engine."""

import pandas as pd

from src.analytics.insights import generate_comprehensive_insights


def test_generate_comprehensive_insights(synthetic_sales_df):
    """Test generating factual insights on synthetic dataset."""
    canonical_df = synthetic_sales_df.rename(
        columns={
            "Sales": "sales",
            "Profit": "profit",
            "Category": "category",
            "Region": "region",
            "Product Name": "product_name",
            "Customer Name": "customer_name",
        }
    )

    insights = generate_comprehensive_insights(canonical_df, currency_label="USD")
    assert len(insights) >= 4

    types = [i.type for i in insights]
    assert "revenue" in types
    assert "profit" in types
    assert "category" in types
    assert "geography" in types

    # Check evidence values in descriptions
    rev_insight = next(i for i in insights if i.type == "revenue")
    assert "$2,454.90" in rev_insight.description


def test_insights_no_fabrication_on_missing_columns():
    """Test that when profit or geography are missing, no fabricated claims are produced."""
    df = pd.DataFrame({
        "sales": [100.0, 200.0, 300.0],
        # Notice: profit, category, region, and customer are absent!
    })

    insights = generate_comprehensive_insights(df)
    types = [i.type for i in insights]

    assert "revenue" in types
    # Must NOT generate fake profit, category, or geography claims!
    assert "profit" not in types
    assert "category" not in types
    assert "geography" not in types
    assert "customer" not in types
