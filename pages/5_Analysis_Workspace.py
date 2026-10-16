"""Step 5: Analysis Workspace & Analytical Readiness."""

import streamlit as st

from src.analytics.aggregations import aggregate_by_category, aggregate_by_time
from src.analytics.insights import generate_foundational_insights
from src.analytics.metrics import calculate_foundational_kpis
from src.config import UIThemeConfig
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_section_heading,
    render_step_indicator,
)
from src.ui.layout import render_app_footer, render_app_header
from src.ui.navigation import (
    get_current_dataset,
    has_active_dataset,
    init_session_state,
    render_step_navigation,
)
from src.utils.formatting import format_currency, format_number, format_percentage
from src.visualization.chart_factory import (
    create_bar_chart,
    create_line_chart,
)

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=5)

render_section_heading(
    title="Sales Analysis Workspace",
    subtitle="Foundational KPIs, initial visualizations, and commercial performance signals.",
    icon="📊",
)

if not has_active_dataset():
    render_empty_state(
        title="No Dataset Loaded for Analysis",
        description="Please upload a sales file or load the sample data to activate the workspace.",
        icon="📂",
    )
    render_step_navigation(
        current_step=5,
        prev_page="pages/4_Column_Mapping.py",
        next_page="pages/6_Reports_and_Export.py",
        can_advance=False,
        blocking_message="Analysis requires an active dataset.",
    )
    render_app_footer()
    st.stop()

# Retrieve standard mapped DataFrame or fallback to raw
standard_df = st.session_state.get("standard_df")
if standard_df is None:
    st.warning("⚠️ Column mapping has not been finalized yet. Displaying unmapped preview.")
    display_df = active_ds.raw_df
else:
    display_df = standard_df

# Compute high level KPIs
kpis = calculate_foundational_kpis(display_df)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card(
        label="Total Revenue",
        value=format_currency(kpis.total_revenue) if kpis.total_revenue is not None else "—",
        sublabel="Gross sales volume",
        icon="💰",
        color=UIThemeConfig.PRIMARY_VIOLET,
    )
with c2:
    render_metric_card(
        label="Total Orders",
        value=format_number(kpis.total_orders),
        sublabel="Unique transaction count",
        icon="🧾",
        color=UIThemeConfig.SECONDARY_CYAN,
    )
with c3:
    render_metric_card(
        label="Average Order Value",
        value=format_currency(kpis.avg_order_value) if kpis.avg_order_value is not None else "—",
        sublabel="Revenue per transaction",
        icon="🏷️",
        color=UIThemeConfig.COLOR_SUCCESS,
    )
with c4:
    prof_sub = (
        f"{format_percentage(kpis.profit_margin_pct)} margin"
        if kpis.profit_margin_pct is not None
        else "Net earnings"
    )
    prof_color = (
        UIThemeConfig.COLOR_DANGER
        if kpis.profit_margin_pct and kpis.profit_margin_pct < 0
        else UIThemeConfig.COLOR_INFO
    )
    render_metric_card(
        label="Total Profit",
        value=format_currency(kpis.total_profit) if kpis.total_profit is not None else "—",
        sublabel=prof_sub,
        icon="📈",
        color=prof_color,
    )

# Foundational Automated Insights
insights = generate_foundational_insights(display_df)
if insights:
    st.markdown("#### Automated Commercial Signals")
    insight_cols = st.columns(min(len(insights), 3))
    for idx, ins in enumerate(insights[:3]):
        with insight_cols[idx]:
            st.markdown(
                f"""
                <div style="background: rgba(17, 24, 39, 0.6); border: 1px solid rgba(255, 255, 255, 0.08);
                            border-radius: 12px; padding: 1rem; height: 100%;">
                    <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">{ins['icon']}</div>
                    <strong style="color: #F9FAFB; font-size: 0.9rem;">{ins['title']}</strong>
                    <p style="color: #9CA3AF; font-size: 0.8rem; margin-top: 0.35rem; line-height: 1.4;">
                        {ins['description']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

# Foundational Visualizations
col_v1, col_v2 = st.columns([1, 1], gap="medium")

with col_v1:
    st.markdown("##### Revenue by Product Category")
    if "category" in display_df.columns and "sales" in display_df.columns:
        cat_df = aggregate_by_category(display_df, cat_col="category", metric_col="sales")
        if not cat_df.empty:
            fig_bar = create_bar_chart(
                cat_df,
                x="category",
                y="sales",
                title="Sales by Category",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No categorical sales records found.")
    else:
        st.info("Category and Sales fields must be mapped to display this visualization.")

with col_v2:
    st.markdown("##### Sales Trend Over Time")
    if "order_date" in display_df.columns and "sales" in display_df.columns:
        time_df = aggregate_by_time(display_df, date_col="order_date", metric_col="sales")
        if not time_df.empty:
            fig_line = create_line_chart(
                time_df,
                x="order_date",
                y="sales",
                title="Monthly Revenue Trend",
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No time series data available.")
    else:
        st.info("Order Date and Sales fields must be mapped to display trend charts.")

# Phase 2 Readiness Notice
st.markdown(
    """
    <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25);
                border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem;">
        <h5 style="color: #F9FAFB; margin: 0 0 0.5rem 0;">🚀 Master Prompt 2 Roadmap: Advanced Analytics Engine</h5>
        <p style="color: #9CA3AF; font-size: 0.85rem; margin: 0; line-height: 1.5;">
            The foundation, data ingestion, column mapping, and visualization factory are active.
            Master Prompt 2 will unlock: dynamic multi-dimensional filters (date range, categories, regions),
            Pareto 80/20 customer distribution, margin erosion analysis by discount tier, geographic chloropleth maps,
            and comparative time-series decomposition.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Bottom Navigation
render_step_navigation(
    current_step=5,
    prev_page="pages/4_Column_Mapping.py",
    next_page="pages/6_Reports_and_Export.py",
    next_label="Proceed to Reports & Export ➡️",
    can_advance=has_active_dataset(),
    blocking_message="Active dataset required to review workspace.",
)

render_app_footer()
