"""Application layout, styling injection, branded header, and footer components."""

import os

import streamlit as st

from src.config import AppConfig, UIThemeConfig


def inject_custom_css() -> None:
    """Inject custom styles into Streamlit without breaking core widgets."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline basic rules
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-color: {UIThemeConfig.BG_DARK};
                    color: {UIThemeConfig.TEXT_PRIMARY};
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def render_app_header(dataset_name: str | None = None, row_count: int = 0) -> None:
    """Render top application brand banner with live dataset status badge."""
    inject_custom_css()

    status_html = ""
    if dataset_name:
        status_html = f"""
        <div style="text-align: right;">
            <span class="badge-pill badge-success">● Active Dataset</span>
            <div style="font-size: 0.85rem; font-weight: 600; color: #F9FAFB; margin-top: 4px;">{dataset_name}</div>
            <div style="font-size: 0.75rem; color: #9CA3AF;">{row_count:,} records loaded</div>
        </div>
        """
    else:
        status_html = """
        <div style="text-align: right;">
            <span class="badge-pill badge-warning">○ No Dataset Loaded</span>
            <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">Upload data or select sample</div>
        </div>
        """

    header_html = f"""
    <div class="app-header-container">
        <div>
            <h1 class="brand-title">{AppConfig.APP_NAME}</h1>
            <p class="brand-tagline">{AppConfig.TAGLINE}</p>
        </div>
        {status_html}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_app_footer() -> None:
    """Render professional footer with attribution, privacy assurance, and phase info."""
    footer_html = f"""
    <div class="app-footer">
        <div>
            <strong>{AppConfig.APP_NAME}</strong> v{AppConfig.VERSION} &nbsp;•&nbsp;
            <span>Designed for sales intelligence and performance visibility.</span>
        </div>
        <div>
            <span>🔒 Local In-Memory Processing &nbsp;•&nbsp; No Data Transmitted to External APIs</span>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
