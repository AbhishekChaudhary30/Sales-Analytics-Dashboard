"""Step 3: Data Inspection & Exploratory Profiling Page."""

import pandas as pd
import streamlit as st

from src.config import UIThemeConfig
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_quality_warnings_box,
    render_section_heading,
    render_step_indicator,
)
from src.ui.layout import render_app_footer, render_app_header, render_html
from src.ui.navigation import (
    get_current_dataset,
    has_active_dataset,
    init_session_state,
    render_step_navigation,
)

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=3)

render_section_heading(
    title="Data Inspection & Health Audit",
    subtitle="Examine structure, missing values, data distributions, and candidate business fields.",
    icon="🔍",
)

if not has_active_dataset():
    render_empty_state(
        title="No Dataset Available for Inspection",
        description="Please upload a sales file in Step 2 or load the sample data in Step 1.",
        icon="📂",
    )
    render_step_navigation(
        current_step=3,
        prev_page="pages/2_Upload_Data.py",
        next_page="pages/4_Column_Mapping.py",
        can_advance=False,
        blocking_message="Cannot inspect data without an active dataset.",
    )
    render_app_footer()
    st.stop()

# Retrieve active dataset and profile
raw_df = active_ds.raw_df
profile = st.session_state.get("dataset_profile")

# Top summary KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card(
        label="Total Records",
        value=f"{len(raw_df):,}",
        sublabel="Rows in memory",
        icon="📋",
        color=UIThemeConfig.PRIMARY_VIOLET,
    )
with c2:
    render_metric_card(
        label="Total Attributes",
        value=f"{len(raw_df.columns)}",
        sublabel="Columns detected",
        icon="🏷️",
        color=UIThemeConfig.SECONDARY_CYAN,
    )
with c3:
    total_missing = int(raw_df.isna().sum().sum())
    total_cells = raw_df.size
    missing_pct = (total_missing / total_cells * 100.0) if total_cells > 0 else 0.0
    miss_color = UIThemeConfig.COLOR_WARNING if missing_pct > 5.0 else UIThemeConfig.COLOR_SUCCESS
    render_metric_card(
        label="Missing Cells",
        value=f"{total_missing:,}",
        sublabel=f"{missing_pct:.2f}% of all cells",
        icon="⚠️",
        color=miss_color,
    )
with c4:
    dup_rows = profile.duplicate_rows_count if profile else 0
    render_metric_card(
        label="Duplicate Rows",
        value=f"{dup_rows:,}",
        sublabel=f"{profile.duplicate_rows_percentage if profile else 0.0:.1f}% rate",
        icon="👥",
        color=UIThemeConfig.COLOR_INFO,
    )

if profile and profile.quality_warnings:
    render_html("<div style='height: 0.75rem;'></div>")
    render_quality_warnings_box(profile.quality_warnings)

# Tabbed detailed exploration
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Raw Data Preview",
    "📊 Column Schema & Types",
    "📈 Numeric Statistics",
    "📅 Date & Category Distributions",
])

with tab1:
    st.markdown("#### Sample Records")
    preview_limit = st.slider("Number of preview rows", min_value=5, max_value=min(100, len(raw_df)), value=15, step=5)
    st.dataframe(
        raw_df.head(preview_limit),
        use_container_width=True,
        height=320,
    )
    st.caption(f"Displaying top {preview_limit} of {len(raw_df):,} records.")

with tab2:
    st.markdown("#### Attribute Telemetry & Inferred Semantic Types")
    col_records = []
    if profile:
        for col, cp in profile.columns_profile.items():
            col_records.append({
                "Column Name": cp.column_name,
                "Inferred Type": cp.semantic_type.capitalize(),
                "Storage Dtype": cp.raw_dtype,
                "Non-Null Count": f"{cp.non_null_count:,}",
                "Missing (%)": f"{cp.missing_percentage:.1f}%",
                "Unique Values": f"{cp.unique_count:,}",
                "Sample Values": ", ".join(cp.sample_values[:3]),
            })

    col_df = pd.DataFrame(col_records)
    st.dataframe(col_df, use_container_width=True, height=350)

with tab3:
    st.markdown("#### Numeric Measures Summary")
    num_cols = profile.candidate_numeric_cols if profile else []
    if num_cols:
        num_records = []
        for col in num_cols:
            cp = profile.columns_profile.get(col)
            if cp and cp.num_mean is not None:
                num_records.append({
                    "Measure": col,
                    "Min": f"{cp.num_min:,.2f}" if cp.num_min is not None else "—",
                    "Q25 (25%)": f"{cp.num_q25:,.2f}" if cp.num_q25 is not None else "—",
                    "Median (50%)": f"{cp.num_median:,.2f}" if cp.num_median is not None else "—",
                    "Mean": f"{cp.num_mean:,.2f}" if cp.num_mean is not None else "—",
                    "Q75 (75%)": f"{cp.num_q75:,.2f}" if cp.num_q75 is not None else "—",
                    "Max": f"{cp.num_max:,.2f}" if cp.num_max is not None else "—",
                    "Std Dev": f"{cp.num_std:,.2f}" if cp.num_std is not None else "—",
                })
        if num_records:
            st.dataframe(pd.DataFrame(num_records), use_container_width=True)
        else:
            st.info("No numeric columns with calculable statistics found.")
    else:
        st.info("No numeric columns detected in this dataset.")

with tab4:
    col_d, col_c = st.columns([1, 1], gap="medium")

    with col_d:
        st.markdown("#### Detected Date Columns")
        date_cols = profile.candidate_datetime_cols if profile else []
        if date_cols:
            date_records = []
            for col in date_cols:
                cp = profile.columns_profile.get(col)
                if cp and cp.date_min:
                    date_records.append({
                        "Date Field": col,
                        "Earliest Date": cp.date_min,
                        "Latest Date": cp.date_max,
                        "Timespan (Days)": f"{cp.date_range_days:,} days",
                    })
            st.dataframe(pd.DataFrame(date_records), use_container_width=True)
        else:
            st.warning("No datetime columns detected automatically. You can map date fields in Step 4.")

    with col_c:
        st.markdown("#### Categorical Cardinality")
        cat_cols = profile.candidate_categorical_cols if profile else []
        if cat_cols:
            selected_cat = st.selectbox("Select categorical attribute to inspect top groups", cat_cols)
            if selected_cat and profile:
                cp = profile.columns_profile.get(selected_cat)
                if cp and cp.top_categories:
                    cat_chart_df = pd.DataFrame(
                        list(cp.top_categories.items()),
                        columns=["Category", "Count"],
                    )
                    st.dataframe(cat_chart_df, use_container_width=True)
        else:
            st.info("No categorical fields detected.")

# Bottom Navigation
render_step_navigation(
    current_step=3,
    prev_page="pages/2_Upload_Data.py",
    next_page="pages/4_Column_Mapping.py",
    next_label="Proceed to Column Mapping ➡️",
    can_advance=has_active_dataset(),
    blocking_message="Active dataset required.",
)

render_app_footer()
