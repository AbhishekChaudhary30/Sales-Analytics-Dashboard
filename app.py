"""Main Application Entry Point.

Configures global layout, registers multipage workflow via st.navigation,
and maintains sidebar status telemetry.
"""

import streamlit as st

from src.config import AppConfig
from src.ui.layout import inject_custom_css, render_html
from src.ui.navigation import get_current_dataset, init_session_state

# Configure Streamlit page parameters
st.set_page_config(
    page_title=AppConfig.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize global session state
init_session_state()

# Inject styling
inject_custom_css()

# Configure Multipage Navigation
pages = [
    st.Page("pages/1_Overview.py", title="1. Overview", icon="🏠"),
    st.Page("pages/2_Upload_Data.py", title="2. Upload Data", icon="📤"),
    st.Page("pages/3_Data_Inspection.py", title="3. Data Inspection", icon="🔍"),
    st.Page("pages/4_Column_Mapping.py", title="4. Column Mapping", icon="🧭"),
    st.Page("pages/5_Analysis_Workspace.py", title="5. Analysis Workspace", icon="📊"),
    st.Page("pages/6_Reports_and_Export.py", title="6. Reports & Export", icon="📑"),
]

pg = st.navigation(pages)

# Render Sidebar metadata
with st.sidebar:
    brand_sidebar_html = (
        '<div style="padding: 0.5rem 0 1rem 0;">'
        '<div style="font-size: 1.15rem; font-weight: 800; color: #F9FAFB; display: flex; align-items: center; gap: 8px;">'
        '📈 <span>Sales Analytics</span>'
        '</div>'
        '<div style="font-size: 0.75rem; color: #8B5CF6; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">'
        'Portfolio Edition v1.0.0'
        '</div>'
        '</div>'
    )
    render_html(brand_sidebar_html)

    # Active dataset indicator in sidebar
    active_ds = get_current_dataset()
    if active_ds is not None:
        ds_status_html = (
            '<div style="background: rgba(17, 24, 39, 0.8); border: 1px solid rgba(16, 185, 129, 0.3); '
            'border-radius: 10px; padding: 0.75rem; margin-bottom: 1rem;">'
            '<span class="badge-pill badge-success" style="font-size: 0.65rem;">Active Dataset</span>'
            f'<div style="font-size: 0.825rem; font-weight: 600; color: #F9FAFB; margin-top: 4px; word-break: break-all;">'
            f'{active_ds.file_name}'
            '</div>'
            f'<div style="font-size: 0.75rem; color: #9CA3AF;">'
            f'{active_ds.total_rows:,} rows &bull; {active_ds.total_cols} cols'
            '</div>'
            '</div>'
        )
        render_html(ds_status_html)
    else:
        no_ds_html = (
            '<div style="background: rgba(17, 24, 39, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); '
            'border-radius: 10px; padding: 0.75rem; margin-bottom: 1rem;">'
            '<span class="badge-pill badge-warning" style="font-size: 0.65rem;">No Data</span>'
            '<div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">'
            'Select sample or upload CSV/XLSX'
            '</div>'
            '</div>'
        )
        render_html(no_ds_html)

# Execute active page
pg.run()
