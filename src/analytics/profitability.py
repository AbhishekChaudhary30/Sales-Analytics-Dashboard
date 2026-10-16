"""Profitability and Discount Analytics.

Analyzes margin health, loss-making transactions, and discount-tier margin erosion.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class LossMakingAnalysis:
    """Findings on unprofitable or loss-making transactions."""

    total_loss_transactions: int
    loss_transaction_rate_pct: float
    total_loss_amount: float
    top_loss_products: pd.DataFrame
    top_loss_categories: pd.DataFrame


@dataclass
class DiscountTierSummary:
    """Performance breakdown across standard commercial discount tiers."""

    tier_df: pd.DataFrame
    correlation_discount_profit: Optional[float]
    high_discount_margin_pct: Optional[float]
    no_discount_margin_pct: Optional[float]


def analyze_loss_making_transactions(
    df: pd.DataFrame,
    profit_col: str = "profit",
    sales_col: str = "sales",
    product_col: str = "product_name",
    category_col: str = "category",
) -> Optional[LossMakingAnalysis]:
    """Examine negative-profit transactions to isolate margin erosion drivers."""
    if df.empty or profit_col not in df.columns:
        return None

    valid_df = df.dropna(subset=[profit_col]).copy()
    valid_df[profit_col] = pd.to_numeric(valid_df[profit_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[profit_col])

    if valid_df.empty:
        return None

    loss_mask = valid_df[profit_col] < 0
    total_losses = int(loss_mask.sum())
    total_rows = len(valid_df)
    loss_rate = round((total_losses / total_rows * 100.0), 2) if total_rows > 0 else 0.0

    loss_df = valid_df[loss_mask]
    total_loss_amt = float(abs(loss_df[profit_col].sum()))

    top_loss_prods = pd.DataFrame()
    if product_col in loss_df.columns:
        top_loss_prods = (
            loss_df.groupby(product_col)[profit_col]
            .sum()
            .reset_index()
            .sort_values(by=profit_col)
            .head(5)
        )

    top_loss_cats = pd.DataFrame()
    if category_col in loss_df.columns:
        top_loss_cats = (
            loss_df.groupby(category_col)[profit_col]
            .sum()
            .reset_index()
            .sort_values(by=profit_col)
        )

    return LossMakingAnalysis(
        total_loss_transactions=total_losses,
        loss_transaction_rate_pct=loss_rate,
        total_loss_amount=total_loss_amt,
        top_loss_products=top_loss_prods,
        top_loss_categories=top_loss_cats,
    )


def analyze_discount_tiers(
    df: pd.DataFrame,
    discount_col: str = "discount",
    sales_col: str = "sales",
    profit_col: str = "profit",
) -> Optional[DiscountTierSummary]:
    """Segment sales into discrete discount bands to test for margin erosion."""
    if df.empty or discount_col not in df.columns:
        return None

    valid_df = df.dropna(subset=[discount_col]).copy()
    valid_df[discount_col] = pd.to_numeric(valid_df[discount_col], errors="coerce")
    valid_df = valid_df.dropna(subset=[discount_col])

    if valid_df.empty:
        return None

    # Normalize discount proportion to percentage (0.15 -> 15.0)
    disc_vals = valid_df[discount_col].copy()
    if disc_vals.max() <= 1.0 and disc_vals.max() > 0:
        disc_pct = disc_vals * 100.0
    else:
        disc_pct = disc_vals

    valid_df["disc_pct"] = disc_pct

    # Define bins
    bins = [-float("inf"), 0.001, 10.001, 20.001, float("inf")]
    labels = ["No Discount (0%)", "Low (1% - 10%)", "Moderate (11% - 20%)", "High (> 20%)"]
    valid_df["discount_tier"] = pd.cut(valid_df["disc_pct"], bins=bins, labels=labels)

    agg_dict: Dict[str, Any] = {"discount_tier": "count"}
    if sales_col in valid_df.columns:
        valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce")
        agg_dict[sales_col] = "sum"

    if profit_col in valid_df.columns:
        valid_df[profit_col] = pd.to_numeric(valid_df[profit_col], errors="coerce")
        agg_dict[profit_col] = "sum"

    grouped = valid_df.groupby("discount_tier", observed=False).agg(
        {k: "sum" if k != "discount_tier" else "count" for k in agg_dict}
    )
    if "discount_tier" in grouped.columns:
        grouped = grouped.rename(columns={"discount_tier": "transaction_count"})
    else:
        grouped.insert(0, "transaction_count", valid_df.groupby("discount_tier", observed=False).size())

    grouped = grouped.reset_index()

    # Calculate profit margin % per tier
    if sales_col in grouped.columns and profit_col in grouped.columns:
        grouped["profit_margin_pct"] = grouped.apply(
            lambda r: round((r[profit_col] / r[sales_col] * 100.0), 2) if r[sales_col] > 0 else None,
            axis=1,
        )

    # Correlation check
    corr_val = None
    if profit_col in valid_df.columns and valid_df["disc_pct"].nunique() > 1 and valid_df[profit_col].nunique() > 1:
        corr_val = round(float(valid_df["disc_pct"].corr(valid_df[profit_col])), 3)

    no_disc_margin = None
    high_disc_margin = None
    if "profit_margin_pct" in grouped.columns:
        row_no = grouped[grouped["discount_tier"] == "No Discount (0%)"]
        if not row_no.empty and pd.notna(row_no["profit_margin_pct"].iloc[0]):
            no_disc_margin = float(row_no["profit_margin_pct"].iloc[0])

        row_high = grouped[grouped["discount_tier"] == "High (> 20%)"]
        if not row_high.empty and pd.notna(row_high["profit_margin_pct"].iloc[0]):
            high_disc_margin = float(row_high["profit_margin_pct"].iloc[0])

    return DiscountTierSummary(
        tier_df=grouped,
        correlation_discount_profit=corr_val,
        high_discount_margin_pct=high_disc_margin,
        no_discount_margin_pct=no_disc_margin,
    )
