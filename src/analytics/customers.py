"""Customer Intelligence, Concentration, and Repeat Purchase Dynamics."""

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


@dataclass
class CustomerConcentration:
    """Findings on revenue concentration among top client accounts."""

    total_customers: int
    total_revenue: float
    top5_revenue: float
    top5_share_pct: float
    top10_revenue: float
    top10_share_pct: float
    concentration_level: str  # 'Low', 'Moderate', 'High'
    average_revenue_per_customer: float


@dataclass
class RepeatCustomerAnalysis:
    """Findings on repeat vs single-time buyer frequency."""

    total_customers: int
    single_order_customers: int
    repeat_customers: int
    repeat_rate_pct: float
    repeat_revenue: float
    repeat_revenue_share_pct: float


def rank_customers(
    df: pd.DataFrame,
    cust_col: str = "customer_name",
    sales_col: str = "sales",
    profit_col: str = "profit",
    order_col: str = "order_id",
    top_n: int = 10,
) -> pd.DataFrame:
    """Rank top purchasing customers with revenue, profit, and order count."""
    if df.empty or cust_col not in df.columns:
        return pd.DataFrame()

    valid_df = df.dropna(subset=[cust_col]).copy()
    if valid_df.empty:
        return pd.DataFrame()

    agg_dict: Dict[str, str] = {}
    if sales_col in valid_df.columns:
        valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce")
        agg_dict[sales_col] = "sum"

    if profit_col in valid_df.columns:
        valid_df[profit_col] = pd.to_numeric(valid_df[profit_col], errors="coerce")
        agg_dict[profit_col] = "sum"

    if order_col in valid_df.columns:
        agg_dict[order_col] = "nunique"

    if not agg_dict:
        return valid_df[cust_col].value_counts().head(top_n).reset_index()

    grouped = valid_df.groupby(cust_col).agg(agg_dict).reset_index()

    if order_col in grouped.columns:
        grouped = grouped.rename(columns={order_col: "orders_count"})

    if sales_col in grouped.columns:
        total_rev = grouped[sales_col].sum()
        grouped["revenue_share_pct"] = (
            (grouped[sales_col] / total_rev * 100.0).round(2) if total_rev > 0 else 0.0
        )
        grouped = grouped.sort_values(by=sales_col, ascending=False)

    return grouped.head(top_n)


def analyze_customer_concentration(
    df: pd.DataFrame,
    cust_col: str = "customer_name",
    sales_col: str = "sales",
) -> Optional[CustomerConcentration]:
    """Calculate commercial concentration among top 5 and top 10 accounts."""
    if df.empty or cust_col not in df.columns or sales_col not in df.columns:
        return None

    valid_df = df.dropna(subset=[cust_col, sales_col]).copy()
    valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce")
    valid_df = valid_df[valid_df[sales_col] > 0]

    if valid_df.empty:
        return None

    grouped = valid_df.groupby(cust_col)[sales_col].sum().sort_values(ascending=False)
    total_cust = len(grouped)
    total_rev = float(grouped.sum())

    if total_cust == 0 or total_rev <= 0:
        return None

    top5_rev = float(grouped.head(5).sum())
    top5_share = round((top5_rev / total_rev * 100.0), 2)

    top10_rev = float(grouped.head(10).sum())
    top10_share = round((top10_rev / total_rev * 100.0), 2)

    if top5_share > 50.0:
        conc_level = "High"
    elif top5_share > 25.0:
        conc_level = "Moderate"
    else:
        conc_level = "Low"

    arpc = round(total_rev / total_cust, 2)

    return CustomerConcentration(
        total_customers=total_cust,
        total_revenue=total_rev,
        top5_revenue=top5_rev,
        top5_share_pct=top5_share,
        top10_revenue=top10_rev,
        top10_share_pct=top10_share,
        concentration_level=conc_level,
        average_revenue_per_customer=arpc,
    )


def analyze_repeat_customers(
    df: pd.DataFrame,
    cust_col: str = "customer_name",
    order_col: str = "order_id",
    sales_col: str = "sales",
) -> Optional[RepeatCustomerAnalysis]:
    """Analyze customer retention and repeat ordering frequency."""
    if df.empty or cust_col not in df.columns:
        return None

    valid_df = df.dropna(subset=[cust_col]).copy()
    if order_col in valid_df.columns:
        counts = valid_df.groupby(cust_col)[order_col].nunique()
    else:
        counts = valid_df.groupby(cust_col).size()

    total_cust = len(counts)
    if total_cust == 0:
        return None

    repeat_mask = counts >= 2
    repeat_cust_count = int(repeat_mask.sum())
    single_cust_count = total_cust - repeat_cust_count
    repeat_rate = round((repeat_cust_count / total_cust * 100.0), 2)

    repeat_rev = 0.0
    repeat_rev_share = 0.0

    if sales_col in valid_df.columns:
        valid_df[sales_col] = pd.to_numeric(valid_df[sales_col], errors="coerce").fillna(0)
        total_rev = valid_df[sales_col].sum()
        repeat_cust_names = set(counts[repeat_mask].index)
        repeat_rev = float(valid_df[valid_df[cust_col].isin(repeat_cust_names)][sales_col].sum())
        if total_rev > 0:
            repeat_rev_share = round((repeat_rev / total_rev * 100.0), 2)

    return RepeatCustomerAnalysis(
        total_customers=total_cust,
        single_order_customers=single_cust_count,
        repeat_customers=repeat_cust_count,
        repeat_rate_pct=repeat_rate,
        repeat_revenue=repeat_rev,
        repeat_revenue_share_pct=repeat_rev_share,
    )
