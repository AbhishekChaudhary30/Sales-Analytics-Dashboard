"""Step 5: Complete Sales Intelligence Workspace & Analytics Engine."""

import streamlit as st

from src.analytics.customers import (
    analyze_customer_concentration,
    analyze_repeat_customers,
    rank_customers,
)
from src.analytics.geography import analyze_geography
from src.analytics.insights import generate_comprehensive_insights
from src.analytics.metrics import compute_all_kpis
from src.analytics.products import (
    analyze_categories,
    calculate_pareto_analysis,
    rank_products,
)
from src.analytics.profitability import (
    analyze_discount_tiers,
    analyze_loss_making_transactions,
)
from src.analytics.statistics import (
    compute_correlation_matrix,
    compute_descriptive_stats,
    detect_iqr_outliers,
)
from src.analytics.time_series import (
    aggregate_time_series,
    calculate_year_over_year,
    compare_periods,
)
from src.config import UIThemeConfig
from src.data.canonical import build_canonical_dataset, check_capability
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_section_heading,
    render_step_indicator,
)
from src.ui.filters import render_filter_sidebar
from src.ui.layout import render_app_footer, render_app_header, render_html
from src.ui.navigation import (
    get_current_dataset,
    has_active_dataset,
    init_session_state,
    render_step_navigation,
)
from src.utils.formatting import (
    format_currency,
    format_number,
    format_percentage,
)
from src.visualization.chart_factory import (
    create_area_chart,
    create_bar_chart,
    create_correlation_heatmap,
    create_donut_chart,
    create_horizontal_bar_chart,
    create_line_chart,
)
from src.visualization.explorer import render_chart_explorer

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=5)

if not has_active_dataset():
    render_empty_state(
        title="No Dataset Available for Analysis",
        description="Please upload a sales file in Step 2 or load the sample data in Step 1 to activate the analytics workspace.",
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

# Ensure ColumnMapper is active
mapper = st.session_state.get("column_mapper")
mappings = mapper.current_mappings if mapper else {}

# Currency & Numbering System Selector in Header Bar
col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
with col_h1:
    render_section_heading(
        title="Sales Intelligence Workspace",
        subtitle="Multi-dimensional commercial analytics, interactive visualizations, and automated insights.",
        icon="📊",
    )

with col_h2:
    selected_currency = st.selectbox(
        "Display Currency",
        options=["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "JPY (¥)", "CAD (C$)", "AUD (A$)"],
        index=0,
        key="currency_selector",
    )
    curr_code = selected_currency.split(" ")[0]

with col_h3:
    use_indian_fmt = st.checkbox(
        "Indian Numbering (L/Cr)",
        value=(curr_code == "INR"),
        key="indian_fmt_toggle",
    )

# Build Canonical Analytics Dataset
canonical_data = build_canonical_dataset(
    raw_df=active_ds.raw_df,
    mappings=mappings,
    currency_label=curr_code,
)
st.session_state["canonical_dataset"] = canonical_data

# Sidebar Filters
filter_state, filter_result = render_filter_sidebar(canonical_data.df)
working_df = filter_result.filtered_df

# Check for empty filter result
if filter_result.is_empty:
    st.warning(
        f"⚠️ Active filters eliminated all {filter_result.total_original:,} records. "
        "Please broaden your filter criteria in the sidebar or click 'Reset All Filters'."
    )
    render_step_navigation(
        current_step=5,
        prev_page="pages/4_Column_Mapping.py",
        next_page="pages/6_Reports_and_Export.py",
        can_advance=False,
    )
    render_app_footer()
    st.stop()

# Store active filtered dataframe in session state for reports
st.session_state["filtered_df"] = working_df

# Compute high-level KPIs
kpi_set = compute_all_kpis(working_df, currency_label=curr_code, use_indian_numbering=use_indian_fmt)

# 10 Dedicated Analytical Tabs
tabs = st.tabs([
    "🏛️ Executive Overview",
    "📈 Sales Trends",
    "📦 Products & Assortment",
    "🗺️ Geography & Territory",
    "👥 Customer Intelligence",
    "⚖️ Profitability & Discounts",
    "🔬 Statistical & Correlations",
    "🎨 Interactive Chart Explorer",
    "🔍 Data Explorer",
    "💡 Automated Insights Center",
])

# --------------------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# --------------------------------------------------------------------------
with tabs[0]:
    st.markdown("#### Commercial Health Snapshot")

    # 4 Top Primary KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        net_kpi = kpi_set.kpi_dict.get("net_sales")
        render_metric_card(
            label=net_kpi.display_name if net_kpi else "Net Revenue",
            value=net_kpi.formatted_value if net_kpi else "—",
            sublabel=net_kpi.sublabel if net_kpi else "",
            icon="💰",
            color=UIThemeConfig.PRIMARY_VIOLET,
        )
    with c2:
        ord_kpi = kpi_set.kpi_dict.get("total_orders")
        render_metric_card(
            label=ord_kpi.display_name if ord_kpi else "Orders",
            value=ord_kpi.formatted_value if ord_kpi else "—",
            sublabel=ord_kpi.sublabel if ord_kpi else "",
            icon="🧾",
            color=UIThemeConfig.SECONDARY_CYAN,
        )
    with c3:
        aov_kpi = kpi_set.kpi_dict.get("avg_order_value")
        render_metric_card(
            label=aov_kpi.display_name if aov_kpi else "AOV",
            value=aov_kpi.formatted_value if aov_kpi else "—",
            sublabel=aov_kpi.sublabel if aov_kpi else "",
            icon="🏷️",
            color=UIThemeConfig.COLOR_SUCCESS,
        )
    with c4:
        prof_kpi = kpi_set.kpi_dict.get("total_profit")
        margin_kpi = kpi_set.kpi_dict.get("profit_margin")
        prof_color = UIThemeConfig.COLOR_DANGER if prof_kpi and prof_kpi.value and prof_kpi.value < 0 else UIThemeConfig.COLOR_INFO
        render_metric_card(
            label=prof_kpi.display_name if prof_kpi else "Net Profit",
            value=prof_kpi.formatted_value if prof_kpi else "—",
            sublabel=margin_kpi.formatted_value + " margin" if margin_kpi and margin_kpi.is_available else "",
            icon="📈",
            color=prof_color,
        )

    # 4 Secondary KPIs
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        qty_kpi = kpi_set.kpi_dict.get("total_quantity")
        render_metric_card(
            label=qty_kpi.display_name if qty_kpi else "Units Sold",
            value=qty_kpi.formatted_value if qty_kpi else "—",
            sublabel=qty_kpi.sublabel if qty_kpi else "",
            icon="📦",
            color="#6366F1",
        )
    with s2:
        cust_kpi = kpi_set.kpi_dict.get("unique_customers")
        render_metric_card(
            label=cust_kpi.display_name if cust_kpi else "Customers",
            value=cust_kpi.formatted_value if cust_kpi else "—",
            sublabel=cust_kpi.sublabel if cust_kpi else "",
            icon="👥",
            color="#EC4899",
        )
    with s3:
        disc_kpi = kpi_set.kpi_dict.get("avg_discount")
        render_metric_card(
            label=disc_kpi.display_name if disc_kpi else "Avg Discount",
            value=disc_kpi.formatted_value if disc_kpi else "—",
            sublabel=disc_kpi.sublabel if disc_kpi else "",
            icon="🏷️",
            color=UIThemeConfig.COLOR_WARNING,
        )
    with s4:
        asp_kpi = kpi_set.kpi_dict.get("avg_selling_price")
        render_metric_card(
            label=asp_kpi.display_name if asp_kpi else "Avg Selling Price",
            value=asp_kpi.formatted_value if asp_kpi else "—",
            sublabel=asp_kpi.sublabel if asp_kpi else "",
            icon="💎",
            color="#14B8A6",
        )

    st.markdown("---")

    # Overview Visuals
    c_left, c_right = st.columns([3, 2], gap="medium")

    with c_left:
        st.markdown("##### Revenue Trajectory")
        cap_trend = check_capability(canonical_data, ["sales", "order_date"], "Revenue Trend")
        if cap_trend.can_execute:
            monthly_ts = aggregate_time_series(working_df, freq="ME")
            if not monthly_ts.empty:
                fig_trend = create_area_chart(monthly_ts, x="order_date", y="sales", title="Monthly Revenue Trend")
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No time series records available under current filters.")
        else:
            st.info(f"ℹ️ {cap_trend.explanation}")

    with c_right:
        st.markdown("##### Category Revenue Share")
        cap_cat = check_capability(canonical_data, ["sales", "category"], "Category Share")
        if cap_cat.can_execute:
            cat_df = analyze_categories(working_df)
            if not cat_df.empty:
                fig_cat = create_donut_chart(cat_df, names="category", values="sales", title="Revenue by Category")
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No categorical sales data available.")
        else:
            st.info(f"ℹ️ {cap_cat.explanation}")

    # Top Executive Insights Preview
    all_insights = generate_comprehensive_insights(working_df, currency_label=curr_code, use_indian_numbering=use_indian_fmt)
    if all_insights:
        st.markdown("##### Executive Observations")
        ins_cols = st.columns(min(len(all_insights), 3))
        for idx, ins in enumerate(all_insights[:3]):
            with ins_cols[idx]:
                card_html = (
                    '<div class="metric-card" style="min-height: 160px;">'
                    '<div class="metric-header">'
                    f'<span class="metric-label">{ins.type.upper()}</span>'
                    f'<span class="metric-icon">{ins.icon}</span>'
                    '</div>'
                    f'<strong style="color: #F9FAFB; font-size: 0.95rem;">{ins.title}</strong>'
                    f'<p style="color: #9CA3AF; font-size: 0.8rem; margin-top: 0.35rem; line-height: 1.4;">'
                    f'{ins.description}'
                    '</p>'
                    '</div>'
                )
                render_html(card_html)

# --------------------------------------------------------------------------
# TAB 2: SALES TRENDS
# --------------------------------------------------------------------------
with tabs[1]:
    st.markdown("#### Temporal Analysis & Trend Intelligence")

    cap_dates = check_capability(canonical_data, ["order_date", "sales"], "Sales Trends")
    if not cap_dates.can_execute:
        st.info(f"ℹ️ {cap_dates.explanation} {cap_dates.alternative_suggestion}")
    else:
        ctrl1, ctrl2, ctrl3 = st.columns(3)
        with ctrl1:
            freq_label = st.selectbox(
                "Aggregation Interval",
                ["Monthly", "Weekly", "Daily", "Quarterly", "Yearly"],
                index=0,
                key="trend_freq",
            )
            freq_code_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Quarterly": "QE", "Yearly": "YE"}
            freq_code = freq_code_map[freq_label]

        with ctrl2:
            trend_measure = st.selectbox(
                "Primary Trend Metric",
                [m for m in ["sales", "profit", "quantity"] if m in working_df.columns],
                index=0,
                key="trend_measure",
            )

        with ctrl3:
            ma_choice = st.selectbox(
                "Moving Average Smoothing",
                ["None", "3-Period Moving Average", "7-Period Moving Average"],
                index=0,
                key="trend_ma",
            )
            ma_window = 3 if "3" in ma_choice else (7 if "7" in ma_choice else None)

        ts_data = aggregate_time_series(
            working_df,
            date_col="order_date",
            metric_col=trend_measure,
            freq=freq_code,
            moving_avg_window=ma_window,
        )

        if not ts_data.empty:
            ma_col = f"{trend_measure}_ma{ma_window}" if ma_window else None
            fig_trend_full = create_line_chart(
                ts_data,
                x="order_date",
                y=trend_measure,
                title=f"{trend_measure.replace('_', ' ').title()} Over Time ({freq_label})",
                secondary_y_col=ma_col,
            )
            st.plotly_chart(fig_trend_full, use_container_width=True)

            # Period-over-Period (PoP) Card
            pop_res = compare_periods(working_df, date_col="order_date", metric_col=trend_measure, freq=freq_code)
            if pop_res and pop_res.previous_value is not None:
                st.markdown("##### Period-over-Period (PoP) Comparison")
                p1, p2, p3 = st.columns(3)
                with p1:
                    render_metric_card(
                        label=f"Current ({pop_res.current_period_label})",
                        value=format_currency(pop_res.current_value, curr_code, use_indian_fmt) if "sales" in trend_measure or "profit" in trend_measure else format_number(pop_res.current_value),
                        sublabel="Active period",
                        icon="📅",
                        color=UIThemeConfig.SECONDARY_CYAN,
                    )
                with p2:
                    render_metric_card(
                        label=f"Previous ({pop_res.previous_period_label})",
                        value=format_currency(pop_res.previous_value, curr_code, use_indian_fmt) if "sales" in trend_measure or "profit" in trend_measure else format_number(pop_res.previous_value),
                        sublabel="Baseline period",
                        icon="⏪",
                        color=UIThemeConfig.PRIMARY_VIOLET,
                    )
                with p3:
                    if pop_res.percentage_change is not None:
                        growth_color = UIThemeConfig.COLOR_SUCCESS if pop_res.percentage_change >= 0 else UIThemeConfig.COLOR_DANGER
                        render_metric_card(
                            label="Period Growth",
                            value=format_percentage(pop_res.percentage_change),
                            sublabel=f"Absolute diff: {format_currency(pop_res.absolute_change, curr_code, use_indian_fmt)}",
                            icon="📈" if pop_res.percentage_change >= 0 else "📉",
                            color=growth_color,
                        )
                    else:
                        render_metric_card(
                            label="Period Growth",
                            value="N/A",
                            sublabel=f"Baseline was zero; Abs diff: {format_currency(pop_res.absolute_change, curr_code, use_indian_fmt)}",
                            icon="⚖️",
                            color=UIThemeConfig.COLOR_WARNING,
                        )

            # Year-over-Year Pivot Table
            st.markdown("##### Year-over-Year (YoY) Monthly Distribution")
            yoy_df = calculate_year_over_year(working_df, date_col="order_date", metric_col=trend_measure)
            if not yoy_df.empty:
                st.dataframe(yoy_df.drop(columns=["month"]), use_container_width=True)
        else:
            st.info("No time series data available for the selected parameters.")

# --------------------------------------------------------------------------
# TAB 3: PRODUCTS & ASSORTMENT
# --------------------------------------------------------------------------
with tabs[2]:
    st.markdown("#### Product Catalog & Assortment Performance")

    cap_prod = check_capability(canonical_data, ["product_name", "sales"], "Product Analytics")
    prod_field = "product_name" if "product_name" in working_df.columns else ("product_id" if "product_id" in working_df.columns else None)

    if not prod_field:
        st.info("ℹ️ Product Name or Product ID is unmapped. Map these fields in Step 4 to unlock product-level intelligence.")
    else:
        p_ctrl1, p_ctrl2, p_ctrl3 = st.columns(3)
        with p_ctrl1:
            prod_metric = st.selectbox(
                "Ranking Measure",
                [m for m in ["sales", "profit", "quantity"] if m in working_df.columns],
                index=0,
                key="prod_ranking_metric",
            )
        with p_ctrl2:
            prod_top_n = st.slider("Number of Products", min_value=5, max_value=30, value=10, step=5, key="prod_top_n_slider")
        with p_ctrl3:
            prod_order = st.selectbox("Sort Direction", ["Highest First (Top Performers)", "Lowest First (Underperformers)"], key="prod_sort_dir")
            is_asc = "Lowest" in prod_order

        ranked_prods = rank_products(
            working_df,
            product_col=prod_field,
            metric_col=prod_metric,
            top_n=prod_top_n,
            ascending=is_asc,
        )

        if not ranked_prods.empty:
            fig_prods = create_horizontal_bar_chart(
                ranked_prods,
                x=prod_metric,
                y=prod_field,
                title=f"{'Top' if not is_asc else 'Bottom'} {prod_top_n} Products by {prod_metric.replace('_', ' ').title()}",
            )
            st.plotly_chart(fig_prods, use_container_width=True)
        else:
            st.info("No product ranking records found.")

        # Pareto 80/20 Analysis
        st.markdown("---")
        st.markdown("##### Pareto Concentration (80/20 Assortment Analysis)")
        pareto_res = calculate_pareto_analysis(working_df, product_col=prod_field)
        if pareto_res:
            pcol1, pcol2 = st.columns([1, 2])
            with pcol1:
                render_metric_card(
                    label="Core 80% Assortment",
                    value=f"{pareto_res.core_product_count} Products",
                    sublabel=f"{pareto_res.core_product_percentage:.1f}% of catalog drives 80% of revenue",
                    icon="🎯",
                    color=UIThemeConfig.PRIMARY_VIOLET,
                )
                render_metric_card(
                    label="Long Tail Catalog",
                    value=f"{pareto_res.total_product_count - pareto_res.core_product_count} Products",
                    sublabel="Generates remaining 20% of revenue",
                    icon="📦",
                    color=UIThemeConfig.SECONDARY_CYAN,
                )
            with pcol2:
                fig_pareto = create_line_chart(
                    pareto_res.pareto_df.head(40),
                    x=prod_field,
                    y="cumulative_pct",
                    title="Cumulative Revenue Curve (Top 40 Products)",
                )
                st.plotly_chart(fig_pareto, use_container_width=True)

        # Category and Subcategory Hierarchy
        if "category" in working_df.columns:
            st.markdown("---")
            st.markdown("##### Merchandise Category Breakdown")
            cat_table = analyze_categories(working_df)
            st.dataframe(cat_table, use_container_width=True)

# --------------------------------------------------------------------------
# TAB 4: GEOGRAPHY & TERRITORY
# --------------------------------------------------------------------------
with tabs[3]:
    st.markdown("#### Geographical & Regional Distribution")

    geo_fields = [f for f in ["region", "state", "city", "country"] if f in working_df.columns]
    if not geo_fields:
        st.info("ℹ️ No geographical fields (Region, Country, State, City) are mapped in the current dataset.")
    else:
        g_ctrl1, g_ctrl2 = st.columns(2)
        with g_ctrl1:
            selected_geo = st.selectbox("Geographical Dimension", geo_fields, index=0, key="geo_dim_select")
        with g_ctrl2:
            geo_metric = st.selectbox(
                "Measure",
                [m for m in ["sales", "profit", "quantity"] if m in working_df.columns],
                index=0,
                key="geo_metric_select",
            )

        geo_df = analyze_geography(working_df, geo_col=selected_geo, sales_col=geo_metric)
        if not geo_df.empty:
            g_fig1, g_fig2 = st.columns([3, 2], gap="medium")
            with g_fig1:
                fig_geo_bar = create_bar_chart(
                    geo_df,
                    x=selected_geo,
                    y=geo_metric,
                    title=f"{geo_metric.replace('_', ' ').title()} across {selected_geo.title()}",
                )
                st.plotly_chart(fig_geo_bar, use_container_width=True)

            with g_fig2:
                st.markdown(f"##### {selected_geo.title()} Rankings")
                st.dataframe(geo_df, use_container_width=True)
        else:
            st.info("No geographical data found under current filters.")

# --------------------------------------------------------------------------
# TAB 5: CUSTOMER INTELLIGENCE
# --------------------------------------------------------------------------
with tabs[4]:
    st.markdown("#### Customer Acquisition, Concentration & Retention")

    cust_col = "customer_name" if "customer_name" in working_df.columns else ("customer_id" if "customer_id" in working_df.columns else None)
    if not cust_col:
        st.info("ℹ️ Customer ID and Customer Name are unmapped. Map customer attributes in Step 4 to view customer insights.")
    else:
        c_conc = analyze_customer_concentration(working_df, cust_col=cust_col)
        c_rep = analyze_repeat_customers(working_df, cust_col=cust_col)

        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        with c_kpi1:
            render_metric_card(
                label="Customer Concentration",
                value=f"{c_conc.top5_share_pct:.1f}%" if c_conc else "—",
                sublabel=f"Top 5 accounts share ({c_conc.concentration_level} risk)" if c_conc else "",
                icon="👥",
                color=UIThemeConfig.COLOR_WARNING if c_conc and c_conc.top5_share_pct > 35 else UIThemeConfig.COLOR_SUCCESS,
            )
        with c_kpi2:
            render_metric_card(
                label="Repeat Customer Rate",
                value=f"{c_rep.repeat_rate_pct:.1f}%" if c_rep else "—",
                sublabel=f"{c_rep.repeat_customers:,} repeat buyers" if c_rep else "",
                icon="🔄",
                color=UIThemeConfig.SECONDARY_CYAN,
            )
        with c_kpi3:
            render_metric_card(
                label="Avg Revenue / Customer",
                value=format_currency(c_conc.average_revenue_per_customer, curr_code, use_indian_fmt) if c_conc else "—",
                sublabel=f"{c_conc.total_customers:,} total buyers" if c_conc else "",
                icon="💰",
                color=UIThemeConfig.PRIMARY_VIOLET,
            )

        st.markdown("---")
        st.markdown("##### Top Purchasing Accounts")
        ranked_custs = rank_customers(working_df, cust_col=cust_col, top_n=10)
        st.dataframe(ranked_custs, use_container_width=True)

# --------------------------------------------------------------------------
# TAB 6: PROFITABILITY & DISCOUNTS
# --------------------------------------------------------------------------
with tabs[5]:
    st.markdown("#### Margin Health & Discount Sensitivity")

    cap_prof = check_capability(canonical_data, ["profit"], "Profitability Analysis")
    if not cap_prof.can_execute:
        st.info(f"ℹ️ {cap_prof.explanation} {cap_prof.alternative_suggestion}")
    else:
        loss_res = analyze_loss_making_transactions(working_df)
        disc_res = analyze_discount_tiers(working_df)

        pf1, pf2, pf3 = st.columns(3)
        with pf1:
            render_metric_card(
                label="Overall Net Profit",
                value=format_currency(kpi_set.total_profit, curr_code, use_indian_fmt),
                sublabel=f"{format_percentage(kpi_set.profit_margin)} net margin",
                icon="📈",
                color=UIThemeConfig.COLOR_SUCCESS if kpi_set.profit_margin and kpi_set.profit_margin > 0 else UIThemeConfig.COLOR_DANGER,
            )
        with pf2:
            render_metric_card(
                label="Unprofitable Orders",
                value=f"{loss_res.total_loss_transactions:,}" if loss_res else "0",
                sublabel=f"{loss_res.loss_transaction_rate_pct:.1f}% of transactions produced net loss" if loss_res else "No loss-making orders",
                icon="⚠️",
                color=UIThemeConfig.COLOR_DANGER if loss_res and loss_res.total_loss_transactions > 0 else UIThemeConfig.COLOR_SUCCESS,
            )
        with pf3:
            render_metric_card(
                label="Cumulative Loss Amount",
                value=format_currency(loss_res.total_loss_amount, curr_code, use_indian_fmt) if loss_res else "$0",
                sublabel="Gross loss value",
                icon="📉",
                color=UIThemeConfig.COLOR_DANGER,
            )

        st.markdown("---")

        # Discount Tier Performance
        if disc_res and not disc_res.tier_df.empty:
            st.markdown("##### Commercial Performance Across Discount Tiers")
            fig_disc_bar = create_bar_chart(
                disc_res.tier_df,
                x="discount_tier",
                y="profit_margin_pct" if "profit_margin_pct" in disc_res.tier_df.columns else "transaction_count",
                title="Profit Margin % by Discount Band",
            )
            st.plotly_chart(fig_disc_bar, use_container_width=True)
            st.dataframe(disc_res.tier_df, use_container_width=True)

        # Loss-making products table
        if loss_res and not loss_res.top_loss_products.empty:
            st.markdown("##### Top Loss-Making Products")
            st.dataframe(loss_res.top_loss_products, use_container_width=True)

# --------------------------------------------------------------------------
# TAB 7: STATISTICAL & CORRELATIONS
# --------------------------------------------------------------------------
with tabs[6]:
    st.markdown("#### Statistical Distributions & Metric Correlations")

    num_cols = [c for c in ["sales", "profit", "quantity", "discount", "unit_price", "cost"] if c in working_df.columns]

    if len(num_cols) < 2:
        st.info("ℹ️ Correlation and distribution analysis requires at least two numeric fields in the dataset.")
    else:
        st.markdown("##### Pearson Metric Correlation Matrix")
        corr_matrix = compute_correlation_matrix(working_df, columns=num_cols)
        if not corr_matrix.empty:
            fig_corr = create_correlation_heatmap(corr_matrix, title="Inter-Metric Correlation Heatmap")
            st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("##### Descriptive Statistical Metrics")
        stats_table = compute_descriptive_stats(working_df, numeric_cols=num_cols)
        st.dataframe(stats_table, use_container_width=True)

        # Outlier Analysis
        if "sales" in working_df.columns:
            st.markdown("##### Outlier Analysis (Interquartile Range Method)")
            outlier_res = detect_iqr_outliers(working_df, column_name="sales")
            if outlier_res:
                st.caption(
                    f"Identified {outlier_res.outlier_count:,} statistical outliers (> {format_currency(outlier_res.upper_bound, curr_code, use_indian_fmt)}) "
                    f"representing {outlier_res.outlier_percentage:.1f}% of transactions."
                )
                if outlier_res.outlier_count > 0:
                    st.dataframe(outlier_res.outlier_rows.head(10), use_container_width=True)

# --------------------------------------------------------------------------
# TAB 8: INTERACTIVE CHART EXPLORER
# --------------------------------------------------------------------------
with tabs[7]:
    st.markdown("#### Self-Service Interactive Chart Explorer")
    render_chart_explorer(working_df)

# --------------------------------------------------------------------------
# TAB 9: DATA EXPLORER
# --------------------------------------------------------------------------
with tabs[8]:
    st.markdown("#### Filtered Transactions Explorer")
    st.caption(f"Displaying {len(working_df):,} filtered transaction line items.")

    search_query = st.text_input("🔍 Quick Search Filtered Records", placeholder="Search by product, customer, order ID...")
    display_subset = working_df
    if search_query:
        mask = working_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_subset = working_df[mask]

    preview_rows = st.slider("Display row limit", min_value=10, max_value=min(200, len(display_subset)), value=25, step=5, key="de_row_limit")
    st.dataframe(display_subset.head(preview_rows), use_container_width=True)

# --------------------------------------------------------------------------
# TAB 10: AUTOMATED INSIGHTS CENTER
# --------------------------------------------------------------------------
with tabs[9]:
    st.markdown("#### Automated Commercial Intelligence Deck")
    st.caption("Evidence-backed findings derived from active dataset calculations without external AI dependencies.")

    if not all_insights:
        st.info("No sufficient evidence available under current filter state to generate automated insights.")
    else:
        for ins in all_insights:
            status_color = (
                UIThemeConfig.COLOR_SUCCESS
                if ins.status == "success"
                else (
                    UIThemeConfig.COLOR_DANGER
                    if ins.status == "danger"
                    else (UIThemeConfig.COLOR_WARNING if ins.status == "warning" else UIThemeConfig.SECONDARY_CYAN)
                )
            )

            rec_html = (
                f'<div style="font-size: 0.8rem; color: #9CA3AF; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.4rem;"><strong>Strategic Takeaway:</strong> {ins.recommendation}</div>'
                if ins.recommendation
                else ""
            )
            insight_card_html = (
                f'<div class="metric-card" style="border-left: 4px solid {status_color}; margin-bottom: 1.25rem;">'
                '<div class="metric-header">'
                f'<span class="metric-label">{ins.type.upper()} &bull; OBSERVED: {ins.observed_value}</span>'
                f'<span class="metric-icon">{ins.icon}</span>'
                '</div>'
                f'<h4 style="color: #F9FAFB; margin: 0.25rem 0 0.5rem 0;">{ins.title}</h4>'
                f'<p style="color: #D1D5DB; font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.5rem;">{ins.description}</p>'
                f'{rec_html}'
                '</div>'
            )
            render_html(insight_card_html)

# Bottom Navigation
render_step_navigation(
    current_step=5,
    prev_page="pages/4_Column_Mapping.py",
    next_page="pages/6_Reports_and_Export.py",
    next_label="Proceed to Reports & Export ➡️",
    can_advance=has_active_dataset(),
)

render_app_footer()
