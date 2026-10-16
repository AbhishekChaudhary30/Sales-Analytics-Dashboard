"""Step 2: Upload Dataset Page."""

import streamlit as st

from src.config import UIThemeConfig
from src.data.column_mapping import ColumnMapper
from src.data.loader import load_dataset
from src.data.profiling import profile_dataset
from src.data.validation import validate_dataset
from src.ui.components import (
    render_metric_card,
    render_quality_warnings_box,
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
from src.utils.errors import format_error_for_ui
from src.utils.formatting import format_filesize

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=2)

render_section_heading(
    title="Upload Sales Dataset",
    subtitle="Select a CSV or Excel file containing transaction, customer, product, or sales records.",
    icon="📤",
)

# Upload container
st.markdown(
    """
    <div style="background: rgba(17, 24, 39, 0.4); border: 1px dashed rgba(139, 92, 246, 0.35);
                border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <p style="color: #9CA3AF; font-size: 0.875rem; margin: 0 0 0.5rem 0;">
            Supported formats: <strong>CSV (.csv)</strong>, <strong>Excel (.xlsx, .xls)</strong>.
            Maximum file size: <strong>50 MB</strong>.
        </p>
        <p style="color: #6B7280; font-size: 0.8rem; margin: 0;">
            🔒 All data is processed strictly in-memory within your local session and is never persisted to disk or sent to external servers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a sales data file",
    type=["csv", "xlsx", "xls"],
    key="file_uploader_widget",
    help="Upload your raw sales spreadsheet or CSV export.",
)

if uploaded_file is not None:
    # Check if newly uploaded file differs from currently loaded dataset
    current_ds = get_current_dataset()
    if current_ds is None or current_ds.file_name != uploaded_file.name:
        with st.spinner(f"Ingesting and validating '{uploaded_file.name}'..."):
            try:
                loaded = load_dataset(uploaded_file, file_name=uploaded_file.name)
                val_res = validate_dataset(loaded.raw_df)

                if not val_res.is_valid:
                    st.error(f"❌ Dataset Validation Failed: {'; '.join(val_res.errors)}")
                else:
                    profile = profile_dataset(loaded.raw_df)
                    mapper = ColumnMapper(list(loaded.raw_df.columns))

                    st.session_state["raw_dataset"] = loaded
                    st.session_state["dataset_profile"] = profile
                    st.session_state["column_mapper"] = mapper
                    st.session_state["sample_loaded"] = False
                    st.session_state["mapping_confirmed"] = False

                    st.toast(f"Successfully loaded '{uploaded_file.name}'!", icon="✅")
                    st.rerun()

            except Exception as e:
                err_dict = format_error_for_ui(e)
                st.error(f"❌ {err_dict['message']}")
                st.info(f"💡 Recommendation: {err_dict['resolution_hint']}")

# Display loaded status card if active
active_ds = get_current_dataset()
profile = st.session_state.get("dataset_profile")

if active_ds is not None and profile is not None:
    st.markdown(
        f"""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 12px; padding: 1.25rem; margin-top: 1rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="badge-pill badge-success">✓ File Ingested Successfully</span>
                    <h4 style="margin: 0.5rem 0 0.25rem 0; color: #F9FAFB;">{active_ds.file_name}</h4>
                    <span style="font-size: 0.85rem; color: #9CA3AF;">
                        Format: {active_ds.file_format.upper()} &nbsp;|&nbsp;
                        Encoding: {active_ds.encoding_used or 'Default'} &nbsp;|&nbsp;
                        Size: {format_filesize(active_ds.file_size_bytes)}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card(
            label="Total Rows",
            value=f"{profile.total_rows:,}",
            sublabel="Transaction line items",
            icon="📄",
            color=UIThemeConfig.PRIMARY_VIOLET,
        )
    with c2:
        render_metric_card(
            label="Total Columns",
            value=f"{profile.total_cols}",
            sublabel="Attributes detected",
            icon="📊",
            color=UIThemeConfig.SECONDARY_CYAN,
        )
    with c3:
        render_metric_card(
            label="Memory Footprint",
            value=profile.memory_formatted,
            sublabel="In-memory RAM usage",
            icon="💾",
            color=UIThemeConfig.COLOR_INFO,
        )
    with c4:
        dup_color = UIThemeConfig.COLOR_WARNING if profile.duplicate_rows_count > 0 else UIThemeConfig.COLOR_SUCCESS
        render_metric_card(
            label="Duplicate Rows",
            value=f"{profile.duplicate_rows_count:,}",
            sublabel=f"{profile.duplicate_rows_percentage:.1f}% duplicates",
            icon="🔍",
            color=dup_color,
        )

    # Show any quality warnings detected during initial ingest
    if profile.quality_warnings:
        render_quality_warnings_box(profile.quality_warnings)

    if st.button("🗑️ Remove Dataset & Reset", key="btn_reset_dataset"):
        st.session_state["raw_dataset"] = None
        st.session_state["dataset_profile"] = None
        st.session_state["column_mapper"] = None
        st.session_state["standard_df"] = None
        st.session_state["current_step"] = 1
        st.rerun()

else:
    st.info("ℹ️ No dataset is currently loaded. Please upload a file above or return to Step 1 to load the sample data.")

# Bottom Navigation
can_proceed = has_active_dataset()
block_msg = "Please upload or select a valid dataset before advancing to Data Inspection."

render_step_navigation(
    current_step=2,
    prev_page="pages/1_Overview.py",
    next_page="pages/3_Data_Inspection.py",
    next_label="Proceed to Data Inspection ➡️",
    can_advance=can_proceed,
    blocking_message=block_msg,
)

render_app_footer()
