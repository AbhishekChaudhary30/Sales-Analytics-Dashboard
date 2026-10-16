"""Dynamic Multi-Dimensional Data Filtering Engine.

Enables unified, schema-aware filtering across time intervals, categories, geographies,
order types, and financial ranges with filter telemetry and safety gating.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Tuple

import pandas as pd


@dataclass
class FilterState:
    """Consolidated state of active analytical filters."""

    date_range: Optional[Tuple[Optional[date], Optional[date]]] = None
    categories: List[str] = field(default_factory=list)
    subcategories: List[str] = field(default_factory=list)
    regions: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    sales_channels: List[str] = field(default_factory=list)
    payment_methods: List[str] = field(default_factory=list)
    min_sales: Optional[float] = None
    max_sales: Optional[float] = None
    transaction_type: str = "All Transactions"  # 'All Transactions', 'Standard Sales Only', 'Returns / Refunds Only'


@dataclass
class FilterResult:
    """Outcome of applying filters to the canonical dataset."""

    filtered_df: pd.DataFrame
    total_original: int
    total_remaining: int
    retention_percentage: float
    active_filters: List[str] = field(default_factory=list)
    is_empty: bool = False


def apply_filters(df: pd.DataFrame, filters: FilterState) -> FilterResult:
    """Filter the working DataFrame based on active criteria without mutating the original data."""
    if df.empty:
        return FilterResult(
            filtered_df=pd.DataFrame(),
            total_original=0,
            total_remaining=0,
            retention_percentage=0.0,
            is_empty=True,
        )

    filtered = df.copy()
    active_summary: List[str] = []
    total_orig = len(df)

    # 1. Date Range Filter
    if filters.date_range and "order_date" in filtered.columns:
        start_d, end_d = filters.date_range
        if start_d is not None and end_d is not None:
            # Ensure order_date is datetime
            if not pd.api.types.is_datetime64_any_dtype(filtered["order_date"]):
                filtered["order_date"] = pd.to_datetime(filtered["order_date"], errors="coerce")

            start_ts = pd.Timestamp(start_d)
            end_ts = pd.Timestamp(end_d) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)

            date_mask = (filtered["order_date"] >= start_ts) & (filtered["order_date"] <= end_ts)
            filtered = filtered[date_mask]
            active_summary.append(f"Date: {start_d} to {end_d}")

    # 2. Categories Filter
    if filters.categories and "category" in filtered.columns:
        filtered = filtered[filtered["category"].astype(str).isin(filters.categories)]
        active_summary.append(f"Categories ({len(filters.categories)})")

    # 3. Subcategories Filter
    if filters.subcategories and "subcategory" in filtered.columns:
        filtered = filtered[filtered["subcategory"].astype(str).isin(filters.subcategories)]
        active_summary.append(f"Subcategories ({len(filters.subcategories)})")

    # 4. Regions Filter
    if filters.regions and "region" in filtered.columns:
        filtered = filtered[filtered["region"].astype(str).isin(filters.regions)]
        active_summary.append(f"Regions ({len(filters.regions)})")

    # 5. States Filter
    if filters.states and "state" in filtered.columns:
        filtered = filtered[filtered["state"].astype(str).isin(filters.states)]
        active_summary.append(f"States ({len(filters.states)})")

    # 6. Sales Channels Filter
    if filters.sales_channels and "sales_channel" in filtered.columns:
        filtered = filtered[filtered["sales_channel"].astype(str).isin(filters.sales_channels)]
        active_summary.append(f"Channels ({len(filters.sales_channels)})")

    # 7. Payment Methods Filter
    if filters.payment_methods and "payment_method" in filtered.columns:
        filtered = filtered[filtered["payment_method"].astype(str).isin(filters.payment_methods)]
        active_summary.append(f"Payment Methods ({len(filters.payment_methods)})")

    # 8. Numeric Sales Min/Max Filter
    if "sales" in filtered.columns:
        valid_sales = pd.to_numeric(filtered["sales"], errors="coerce")
        if filters.min_sales is not None:
            filtered = filtered[valid_sales >= filters.min_sales]
            active_summary.append(f"Min Sales: {filters.min_sales:,.0f}")
        if filters.max_sales is not None:
            filtered = filtered[valid_sales <= filters.max_sales]
            active_summary.append(f"Max Sales: {filters.max_sales:,.0f}")

    # 9. Transaction Type Filter (Positive vs Returns)
    if "sales" in filtered.columns and filters.transaction_type != "All Transactions":
        sales_vals = pd.to_numeric(filtered["sales"], errors="coerce")
        if filters.transaction_type == "Standard Sales Only":
            filtered = filtered[sales_vals >= 0]
            active_summary.append("Positive Sales Only")
        elif filters.transaction_type == "Returns / Refunds Only":
            filtered = filtered[sales_vals < 0]
            active_summary.append("Returns / Refunds Only")

    rem = len(filtered)
    ret_pct = round((rem / total_orig * 100.0), 1) if total_orig > 0 else 0.0

    return FilterResult(
        filtered_df=filtered,
        total_original=total_orig,
        total_remaining=rem,
        retention_percentage=ret_pct,
        active_filters=active_summary,
        is_empty=(rem == 0),
    )
