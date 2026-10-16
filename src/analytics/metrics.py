"""Foundational business metric computations for sales performance."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class SummaryKPIs:
    """Core financial and operational indicators."""

    total_revenue: float | None = None
    total_orders: int | None = None
    total_units: float | None = None
    avg_order_value: float | None = None
    total_profit: float | None = None
    profit_margin_pct: float | None = None
    avg_discount_pct: float | None = None
    unique_customers: int | None = None
    unique_products: int | None = None


def calculate_foundational_kpis(df: pd.DataFrame) -> SummaryKPIs:
    """Compute high-level KPIs based on available standard or mapped fields.

    Operates robustly on partial data without failing if optional columns are absent.
    """
    if df.empty:
        return SummaryKPIs()

    kpi = SummaryKPIs()

    # Total Revenue
    if "sales" in df.columns:
        sales_clean = pd.to_numeric(df["sales"], errors="coerce").dropna()
        kpi.total_revenue = float(sales_clean.sum())

    # Orders count
    if "order_id" in df.columns:
        kpi.total_orders = int(df["order_id"].nunique(dropna=True))
    else:
        kpi.total_orders = len(df)

    # Units sold
    if "quantity" in df.columns:
        qty_clean = pd.to_numeric(df["quantity"], errors="coerce").dropna()
        kpi.total_units = float(qty_clean.sum())

    # Average Order Value (AOV)
    if kpi.total_revenue is not None and kpi.total_orders and kpi.total_orders > 0:
        kpi.avg_order_value = kpi.total_revenue / kpi.total_orders

    # Profit & Margin
    if "profit" in df.columns:
        profit_clean = pd.to_numeric(df["profit"], errors="coerce").dropna()
        kpi.total_profit = float(profit_clean.sum())
        if kpi.total_revenue and kpi.total_revenue > 0:
            kpi.profit_margin_pct = (kpi.total_profit / kpi.total_revenue) * 100.0

    # Discount
    if "discount" in df.columns:
        disc_clean = pd.to_numeric(df["discount"], errors="coerce").dropna()
        if not disc_clean.empty:
            mean_disc = float(disc_clean.mean())
            # If discount is stored as a fraction (0.15), convert to percentage
            if 0.0 < mean_disc <= 1.0:
                mean_disc *= 100.0
            kpi.avg_discount_pct = mean_disc

    # Unique customers
    if "customer_id" in df.columns:
        kpi.unique_customers = int(df["customer_id"].nunique(dropna=True))
    elif "customer_name" in df.columns:
        kpi.unique_customers = int(df["customer_name"].nunique(dropna=True))

    # Unique products
    if "product_name" in df.columns:
        kpi.unique_products = int(df["product_name"].nunique(dropna=True))
    elif "product_id" in df.columns:
        kpi.unique_products = int(df["product_id"].nunique(dropna=True))

    return kpi
