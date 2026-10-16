"""Tests for Product Rankings, Category Aggregations, and Pareto 80/20 Engine."""

import pandas as pd

from src.analytics.products import (
    analyze_categories,
    calculate_pareto_analysis,
    rank_products,
)


def test_rank_products_descending_and_ascending():
    """Test ranking products with top N limits and contribution percentage."""
    df = pd.DataFrame({
        "product_name": ["Widget A", "Widget B", "Widget C", "Widget D"],
        "sales": [500.0, 300.0, 150.0, 50.0],
    })

    top2 = rank_products(df, product_col="product_name", metric_col="sales", top_n=2, ascending=False)
    assert len(top2) == 2
    assert top2.iloc[0]["product_name"] == "Widget A"
    assert top2.iloc[0]["contribution_pct"] == 50.0

    bottom1 = rank_products(df, product_col="product_name", metric_col="sales", top_n=1, ascending=True)
    assert len(bottom1) == 1
    assert bottom1.iloc[0]["product_name"] == "Widget D"


def test_analyze_categories():
    """Test category revenue rollup and margin computation."""
    df = pd.DataFrame({
        "category": ["Tech", "Tech", "Office"],
        "sales": [1000.0, 500.0, 500.0],
        "profit": [200.0, 100.0, 50.0],
    })
    cat_df = analyze_categories(df)

    assert len(cat_df) == 2
    tech_row = cat_df[cat_df["category"] == "Tech"].iloc[0]
    assert tech_row["sales"] == 1500.0
    assert tech_row["revenue_share_pct"] == 75.0
    assert tech_row["profit_margin_pct"] == 20.0


def test_calculate_pareto_analysis():
    """Test Pareto 80/20 analysis calculating core product concentration."""
    # 10 products where product 1 & 2 generate 85% of revenue
    sales_vals = [500.0, 350.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 15.0, 15.0]
    df = pd.DataFrame({
        "product_name": [f"Item_{i}" for i in range(10)],
        "sales": sales_vals,
    })
    pareto = calculate_pareto_analysis(df, product_col="product_name", sales_col="sales", target_pct=80.0)

    assert pareto is not None
    assert pareto.core_product_count == 2
    assert pareto.total_product_count == 10
    assert pareto.core_product_percentage == 20.0
    assert pareto.total_revenue == 1000.0
