"""Step 6: Reports & Export Foundation Page."""

import json

import streamlit as st

from src.ui.components import (
    render_empty_state,
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

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=6)

render_section_heading(
    title="Reports & Data Export",
    subtitle="Export cleaned schemas, analytical summaries, and data profiles for downstream reporting.",
    icon="📑",
)

if not has_active_dataset():
    render_empty_state(
        title="No Data Available for Export",
        description="Please load or upload a sales dataset first.",
        icon="📂",
    )
    render_step_navigation(
        current_step=6,
        prev_page="pages/5_Analysis_Workspace.py",
        next_page=None,
        can_advance=False,
    )
    render_app_footer()
    st.stop()

# Retrieve dataset references
std_df = st.session_state.get("standard_df")
raw_df = active_ds.raw_df
profile = st.session_state.get("dataset_profile")

export_target_df = std_df if std_df is not None else raw_df

st.markdown("#### Available Data Exports")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="metric-card" style="border-left: 4px solid #8B5CF6;">
            <div class="metric-header">
                <span class="metric-label">Processed Dataset</span>
                <span class="metric-icon">📥</span>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.5rem;">
                Standardized CSV
            </div>
            <p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">
                Export cleansed transactions aligned with internal business fields and normalized numbers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    csv_buffer = export_target_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Standardized CSV",
        data=csv_buffer,
        file_name="standardized_sales_data.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )

with c2:
    st.markdown(
        """
        <div class="metric-card" style="border-left: 4px solid #06B6D4;">
            <div class="metric-header">
                <span class="metric-label">Audit Report</span>
                <span class="metric-icon">🔍</span>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.5rem;">
                Data Profile Telemetry
            </div>
            <p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">
                Download structural audit metrics, column distributions, and missing cell statistics as JSON.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    profile_dict = {
        "dataset_name": active_ds.file_name,
        "total_rows": profile.total_rows if profile else len(raw_df),
        "total_columns": profile.total_cols if profile else len(raw_df.columns),
        "duplicate_rows": profile.duplicate_rows_count if profile else 0,
        "quality_warnings": profile.quality_warnings if profile else [],
    }
    json_bytes = json.dumps(profile_dict, indent=2).encode("utf-8")
    st.download_button(
        label="Download Profile JSON",
        data=json_bytes,
        file_name="data_profile_summary.json",
        mime="application/json",
        use_container_width=True,
    )

with c3:
    st.markdown(
        """
        <div class="metric-card" style="border-left: 4px solid #10B981;">
            <div class="metric-header">
                <span class="metric-label">Executive Briefing</span>
                <span class="metric-icon">📊</span>
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.5rem;">
                Analytical PDF Brief
            </div>
            <p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">
                Structured multi-page PDF briefing with executive summary, KPIs, and chart figures.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "Generate Executive PDF (Phase 2)",
        key="btn_pdf_phase2",
        disabled=True,
        help="Full PDF generation engine will be implemented in Master Prompt 2 & 3.",
        use_container_width=True,
    )

# Bottom Navigation
render_step_navigation(
    current_step=6,
    prev_page="pages/5_Analysis_Workspace.py",
    next_page="pages/1_Overview.py",
    next_label="Return to Overview 🏠",
    can_advance=True,
)

render_app_footer()
