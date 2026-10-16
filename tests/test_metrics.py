"""Tests for foundational KPI metrics, time-series aggregations, and business insights."""

import pandas as pd

from src.analytics.aggregations import aggregate_by_category
from src.analytics.insights import generate_foundational_insights
from src.analytics.metrics import calculate_foundational_kpis
from src.data.column_mapping import ColumnMapper, create_standard_dataframe


def test_calculate_foundational_kpis(synthetic_sales_df):
    """Test calculating KPIs on a mapped dataset."""
    mapper = ColumnMapper(list(synthetic_sales_df.columns))
    std_df = create_standard_dataframe(synthetic_sales_df, mapper.current_mappings)

    kpis = calculate_foundational_kpis(std_df)

    assert kpis.total_revenue is not None
    assert round(kpis.total_revenue, 2) == 2454.90
    assert kpis.total_orders == 5
    assert kpis.total_units == 13
    assert kpis.total_profit is not None
    assert round(kpis.total_profit, 2) == 312.60
    assert kpis.profit_margin_pct is not None
    assert kpis.profit_margin_pct > 0


def test_calculate_kpis_empty_df():
    """Test that calculating KPIs on an empty dataframe returns safe None/0 values without raising."""
    empty_df = pd.DataFrame()
    kpis = calculate_foundational_kpis(empty_df)
    assert kpis.total_revenue is None
    assert kpis.total_orders is None


def test_aggregate_by_category(synthetic_sales_df):
    """Test aggregation by category."""
    mapper = ColumnMapper(list(synthetic_sales_df.columns))
    std_df = create_standard_dataframe(synthetic_sales_df, mapper.current_mappings)

    cat_df = aggregate_by_category(std_df, cat_col="category", metric_col="sales")
    assert not cat_df.empty
    assert "Technology" in cat_df["category"].values


def test_generate_foundational_insights(synthetic_sales_df):
    """Test automated heuristic insight generation."""
    mapper = ColumnMapper(list(synthetic_sales_df.columns))
    std_df = create_standard_dataframe(synthetic_sales_df, mapper.current_mappings)

    insights = generate_foundational_insights(std_df)
    assert len(insights) >= 2
    types = [i["type"] for i in insights]
    assert "summary" in types
    assert "profit" in types
