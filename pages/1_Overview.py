"""Step 1: Welcome & Overview Page."""

import os

import streamlit as st

from src.config import AppConfig, UIThemeConfig
from src.data.column_mapping import ColumnMapper
from src.data.loader import load_dataset
from src.data.profiling import profile_dataset
from src.data.validation import validate_dataset
from src.ui.components import (
    render_metric_card,
    render_section_heading,
    render_step_indicator,
)
from src.ui.layout import render_app_footer, render_app_header, render_html
from src.ui.navigation import (
    get_current_dataset,
    init_session_state,
    render_step_navigation,
)

init_session_state()

# Dataset status for header
active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=1)

# Hero section
hero_html = (
    '<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%); '
    'border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 16px; padding: 2rem; margin-bottom: 2rem;">'
    '<h2 style="font-size: 1.75rem; margin-bottom: 0.75rem; color: #F9FAFB;">'
    'Transform Raw Sales Data into High-Impact Commercial Intelligence'
    '</h2>'
    '<p style="color: #D1D5DB; font-size: 1.05rem; line-height: 1.6; max-width: 850px; margin-bottom: 1.5rem;">'
    'Whether you operate an e-commerce storefront, retail chain, or B2B enterprise, '
    'this workspace helps you uncover revenue drivers, customer dynamics, regional trends, '
    'and margin erosion — without requiring proprietary data structures or fixed CSV templates.'
    '</p>'
    '<div style="display: flex; gap: 1rem; flex-wrap: wrap;">'
    '<span class="badge-pill badge-info">✓ Multi-Format (CSV, XLSX)</span>'
    '<span class="badge-pill badge-info">✓ Schema Agnostic & Auto-Mapping</span>'
    '<span class="badge-pill badge-info">✓ In-Memory & Privacy First</span>'
    '<span class="badge-pill badge-info">✓ Interactive Plotly Reports</span>'
    '</div>'
    '</div>'
)
render_html(hero_html)

# Call to Action Options
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    sample_card_html = (
        '<div class="metric-card" style="border-left: 4px solid #8B5CF6; min-height: 220px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Quick Demonstration</span>'
        '<span class="metric-icon">🚀</span>'
        '</div>'
        '<div style="font-size: 1.25rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.5rem;">'
        'Try Sample Superstore Data'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.875rem; line-height: 1.5; margin-bottom: 1.25rem;">'
        'Explore all analytical features immediately using our bundled 150-transaction '
        'retail dataset with categories, customers, profits, discounts, and regional coordinates.'
        '</p>'
        '</div>'
    )
    render_html(sample_card_html)
    if st.button("🚀 Load Sample Superstore Dataset", key="btn_load_sample", use_container_width=True, type="primary"):
        sample_path = os.path.join(os.path.dirname(__file__), "..", AppConfig.DEFAULT_SAMPLE_PATH)
        if os.path.exists(sample_path):
            with st.spinner("Ingesting and profiling sample dataset..."):
                try:
                    loaded = load_dataset(sample_path, file_name="superstore_sample.csv")
                    val_res = validate_dataset(loaded.raw_df)
                    profile = profile_dataset(loaded.raw_df)
                    mapper = ColumnMapper(list(loaded.raw_df.columns))

                    st.session_state["raw_dataset"] = loaded
                    st.session_state["dataset_profile"] = profile
                    st.session_state["column_mapper"] = mapper
                    st.session_state["sample_loaded"] = True
                    st.session_state["current_step"] = 3

                    st.success("✅ Sample dataset loaded successfully! Advancing to Data Inspection...")
                    st.switch_page("pages/3_Data_Inspection.py")
                except Exception as e:
                    st.error(f"Error loading sample file: {e!s}")
        else:
            st.error(f"Sample file not found at expected path: {sample_path}")

with col_right:
    custom_card_html = (
        '<div class="metric-card" style="border-left: 4px solid #06B6D4; min-height: 220px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Custom Dataset</span>'
        '<span class="metric-icon">📤</span>'
        '</div>'
        '<div style="font-size: 1.25rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.5rem;">'
        'Upload Your Own Sales File'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.875rem; line-height: 1.5; margin-bottom: 1.25rem;">'
        'Bring your own sales, invoice, or CRM export in CSV or Excel format. '
        'Our intelligent column mapping engine will detect your business fields automatically.'
        '</p>'
        '</div>'
    )
    render_html(custom_card_html)
    if st.button("📤 Upload Custom Dataset", key="btn_goto_upload", use_container_width=True):
        st.session_state["current_step"] = 2
        st.switch_page("pages/2_Upload_Data.py")

# Workspace Capabilities Section
render_section_heading(
    title="What This Dashboard Analyzes",
    subtitle="Engineered for data compatibility across heterogeneous sales schemas.",
    icon="🔍",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card(
        label="Revenue & KPIs",
        value="Sales Dynamics",
        sublabel="Gross volume, AOV, order rates",
        icon="💳",
        color=UIThemeConfig.PRIMARY_VIOLET,
    )
with c2:
    render_metric_card(
        label="Margins & Profit",
        value="Profitability",
        sublabel="Net profit, margin %, discounts",
        icon="📊",
        color=UIThemeConfig.SECONDARY_CYAN,
    )
with c3:
    render_metric_card(
        label="Products & Categories",
        value="Assortment",
        sublabel="Top performers, Pareto 80/20",
        icon="📦",
        color=UIThemeConfig.COLOR_SUCCESS,
    )
with c4:
    render_metric_card(
        label="Markets & Territory",
        value="Geography",
        sublabel="Regional share, city rankings",
        icon="🗺️",
        color=UIThemeConfig.COLOR_WARNING,
    )

# Step navigation
render_step_navigation(
    current_step=1,
    prev_page=None,
    next_page="pages/2_Upload_Data.py",
    next_label="Continue to Step 2: Upload Data ➡️",
    can_advance=True,
)

render_app_footer()
