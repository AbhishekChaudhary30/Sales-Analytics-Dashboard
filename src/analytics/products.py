"""Product, Category, and Merchandise Hierarchy Performance Analytics.

Includes Top/Bottom rankings, contribution shares, margin analysis, and Pareto 80/20 distributions.
"""

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


@dataclass
class ParetoResult:
    """Findings from Pareto (80/20) cumulative concentration analysis."""

    pareto_df: pd.DataFrame
    core_product_count: int
    total_product_count: int
    core_product_percentage: float
    target_revenue_percentage: float = 80.0
    total_revenue: float = 0.0


def rank_products(
    df: pd.DataFrame,
    product_col: str = "product_name",
    metric_col: str = "sales",
    top_n: int = 10,
    ascending: bool = False,
) -> pd.DataFrame:
    """Rank products by chosen metric (Sales, Profit, Quantity), handling ties consistently."""
    if df.empty or product_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[product_col, metric_col]).copy()
    valid_df[metric_col] = pd.to_numeric(valid_df[metric_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[metric_col])

    if valid_df.empty:
        return pd.DataFrame()

    # Aggregate by product
    grouped = (
        valid_df.groupby(product_col)[metric_col]
        .sum()
        .reset_index()
        .sort_values(by=metric_col, ascending=ascending)
    )

    # Compute contribution percentage of total
    total_val = grouped[metric_col].sum()
    if total_val != 0:
        grouped["contribution_pct"] = (grouped[metric_col] / total_val * 100.0).round(2)
    else:
        grouped["contribution_pct"] = 0.0

    return grouped.head(top_n)


def analyze_categories(
    df: pd.DataFrame,
    category_col: str = "category",
    sales_col: str = "sales",
    profit_col: str = "profit",
    qty_col: str = "quantity",
) -> pd.DataFrame:
    """Generate comprehensive category breakdown with revenue, profit, quantity, and margins."""
    if df.empty or category_col not in df.columns:
        return pd.DataFrame()

    agg_dict: Dict[str, str] = {}
    if sales_col in df.columns:
        agg_dict[sales_col] = "sum"
    if profit_col in df.columns:
        agg_dict[profit_col] = "sum"
    if qty_col in df.columns:
        agg_dict[qty_col] = "sum"

    if not agg_dict:
        # Just count occurrences
        return df[category_col].value_counts().reset_index()

    grouped = df.groupby(category_col).agg(agg_dict).reset_index()

    # Margin % if both sales and profit are present
    if sales_col in grouped.columns and profit_col in grouped.columns:
        total_rev = grouped[sales_col].sum()
        grouped["revenue_share_pct"] = (
            (grouped[sales_col] / total_rev * 100.0).round(2) if total_rev > 0 else 0.0
        )
        grouped["profit_margin_pct"] = grouped.apply(
            lambda r: round((r[profit_col] / r[sales_col] * 100.0), 2) if r[sales_col] > 0 else None,
            axis=1,
        )

    if sales_col in grouped.columns:
        grouped = grouped.sort_values(by=sales_col, ascending=False)

    return grouped


def calculate_pareto_analysis(
    df: pd.DataFrame,
    product_col: str = "product_name",
    sales_col: str = "sales",
    target_pct: float = 80.0,
) -> Optional[ParetoResult]:
    """Execute Pareto 80/20 concentration analysis to identify core drivers of revenue."""
    if df.empty or product_col not in df.columns or sales_col not in df.columns:
        return None

    valid_df = df.dropna(subset=[product_col, sales_col]).copy()
    valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce")
    valid_df = valid_df[valid_df[sales_col] > 0]  # Only consider positive revenue for Pareto

    if valid_df.empty:
        return None

    # Group and sort descending
    grouped = (
        valid_df.groupby(product_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(by=sales_col, ascending=False)
    )

    total_rev = float(grouped[sales_col].sum())
    if total_rev <= 0:
        return None

    grouped["cumulative_revenue"] = grouped[sales_col].cumsum()
    grouped["cumulative_pct"] = (grouped["cumulative_revenue"] / total_rev * 100.0).round(2)

    # Core products reaching target percentage (e.g. 80%)
    core_mask = grouped["cumulative_pct"] <= target_pct
    # Include the boundary product that crosses the threshold
    boundary_idx = grouped[~core_mask].index.min()
    if pd.notna(boundary_idx):
        core_mask.loc[:boundary_idx] = True

    core_count = int(core_mask.sum())
    total_count = len(grouped)
    core_pct = round((core_count / total_count * 100.0), 1) if total_count > 0 else 0.0

    return ParetoResult(
        pareto_df=grouped,
        core_product_count=core_count,
        total_product_count=total_count,
        core_product_percentage=core_pct,
        target_revenue_percentage=target_pct,
        total_revenue=total_rev,
    )
