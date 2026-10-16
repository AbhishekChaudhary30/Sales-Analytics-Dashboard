"""Geographical and Territory Sales Performance Analytics.

Supports hierarchical aggregation across Region, Country, State, and City dimensions.
"""

from typing import Any, Dict

import pandas as pd


def analyze_geography(
    df: pd.DataFrame,
    geo_col: str = "region",
    sales_col: str = "sales",
    profit_col: str = "profit",
    qty_col: str = "quantity",
    order_col: str = "order_id",
) -> pd.DataFrame:
    """Aggregate multi-metric commercial performance across a geographical dimension."""
    if df.empty or geo_col not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[geo_col]).copy()
    if valid_df.empty:
        return pd.DataFrame()

    agg_dict: Dict[str, Any] = {}
    if sales_col in valid_df.columns:
        valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce")
        agg_dict[sales_col] = "sum"

    if profit_col in valid_df.columns:
        valid_df[profit_col] = pd.to_numeric(valid_df[profit_col], errors="coerce")
        agg_dict[profit_col] = "sum"

    if qty_col in valid_df.columns:
        valid_df[qty_col] = pd.to_numeric(valid_df[qty_col], errors="coerce")
        agg_dict[qty_col] = "sum"

    if order_col in valid_df.columns:
        agg_dict[order_col] = "nunique"

    if not agg_dict:
        return valid_df[geo_col].value_counts().reset_index()

    grouped = valid_df.groupby(geo_col).agg(agg_dict).reset_index()

    # Column renames
    if order_col in grouped.columns:
        grouped = grouped.rename(columns={order_col: "orders_count"})

    # Compute Revenue Share % and Profit Margin %
    if sales_col in grouped.columns:
        total_rev = grouped[sales_col].sum()
        grouped["revenue_share_pct"] = (
            (grouped[sales_col] / total_rev * 100.0).round(2) if total_rev > 0 else 0.0
        )

        if profit_col in grouped.columns:
            grouped["profit_margin_pct"] = grouped.apply(
                lambda r: round((r[profit_col] / r[sales_col] * 100.0), 2) if r[sales_col] > 0 else None,
                axis=1,
            )

        grouped = grouped.sort_values(by=sales_col, ascending=False)

    return grouped
