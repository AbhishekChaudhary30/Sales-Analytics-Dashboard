"""Dynamic Filter UI Component for Streamlit Sidebar & Header Controls."""

from typing import Tuple

import pandas as pd
import streamlit as st

from src.analytics.filters import FilterResult, FilterState, apply_filters
from src.ui.layout import render_html


def render_filter_sidebar(df: pd.DataFrame) -> Tuple[FilterState, FilterResult]:
    """Render interactive schema-aware filter controls in the Streamlit sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Analytical Filters")

    if df.empty:
        st.sidebar.info("No active dataset to filter.")
        return FilterState(), FilterResult(pd.DataFrame(), 0, 0, 0.0, [], is_empty=True)

    filter_state = FilterState()

    # 1. Date Range Picker
    if "order_date" in df.columns:
        date_series = pd.to_datetime(df["order_date"], errors="coerce").dropna()
        if not date_series.empty:
            min_d = date_series.min().date()
            max_d = date_series.max().date()
            if min_d < max_d:
                selected_dates = st.sidebar.date_input(
                    "📅 Order Date Range",
                    value=(min_d, max_d),
                    min_value=min_d,
                    max_value=max_d,
                    key="filter_date_range",
                )
                if isinstance(selected_dates, (tuple, list)):
                    if len(selected_dates) == 2:
                        filter_state.date_range = (selected_dates[0], selected_dates[1])
                    elif len(selected_dates) == 1:
                        filter_state.date_range = (selected_dates[0], selected_dates[0])

    # 2. Category Filter
    if "category" in df.columns:
        cats = sorted([str(c) for c in df["category"].dropna().unique()])
        if cats:
            selected_cats = st.sidebar.multiselect(
                "📦 Categories",
                options=cats,
                default=[],
                placeholder="All Categories",
                key="filter_categories",
            )
            filter_state.categories = selected_cats

    # 3. Region Filter
    if "region" in df.columns:
        regions = sorted([str(r) for r in df["region"].dropna().unique()])
        if regions:
            selected_regions = st.sidebar.multiselect(
                "🗺️ Regions",
                options=regions,
                default=[],
                placeholder="All Regions",
                key="filter_regions",
            )
            filter_state.regions = selected_regions

    # 4. Sales Channel / Segment Filter
    channel_col = "sales_channel" if "sales_channel" in df.columns else ("segment" if "segment" in df.columns else None)
    if channel_col:
        channels = sorted([str(ch) for ch in df[channel_col].dropna().unique()])
        if channels:
            selected_channels = st.sidebar.multiselect(
                f"🏷️ {channel_col.replace('_', ' ').title()}",
                options=channels,
                default=[],
                placeholder=f"All {channel_col.title()}s",
                key="filter_channels",
            )
            filter_state.sales_channels = selected_channels

    # 5. Transaction Type (Positive vs Returns)
    if "sales" in df.columns:
        sales_numeric = pd.to_numeric(df["sales"], errors="coerce").dropna()
        has_returns = bool((sales_numeric < 0).any())
        if has_returns:
            tx_type = st.sidebar.radio(
                "🧾 Transaction Filter",
                ["All Transactions", "Standard Sales Only", "Returns / Refunds Only"],
                index=0,
                key="filter_tx_type",
            )
            filter_state.transaction_type = tx_type

    # Reset button
    if st.sidebar.button("🔄 Reset All Filters", key="btn_reset_filters", use_container_width=True):
        st.session_state["filter_date_range"] = ()
        st.session_state["filter_categories"] = []
        st.session_state["filter_regions"] = []
        if "filter_channels" in st.session_state:
            st.session_state["filter_channels"] = []
        if "filter_tx_type" in st.session_state:
            st.session_state["filter_tx_type"] = "All Transactions"
        st.rerun()

    # Apply filters
    filter_result = apply_filters(df, filter_state)

    # Telemetry banner in sidebar
    banner_html = (
        '<div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); '
        'border-radius: 8px; padding: 0.6rem; margin-top: 0.75rem; font-size: 0.8rem; color: #9CA3AF;">'
        f'Active Records: <strong>{filter_result.total_remaining:,}</strong> / {filter_result.total_original:,} '
        f'({filter_result.retention_percentage:.1f}%)'
        '</div>'
    )
    with st.sidebar:
        render_html(banner_html)

    return filter_state, filter_result
