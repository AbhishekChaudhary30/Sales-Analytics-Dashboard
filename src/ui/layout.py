"""Application layout, styling injection, branded header, and footer components."""

import os
import textwrap

import streamlit as st

from src.config import AppConfig, UIThemeConfig


def render_html(html_content: str) -> None:
    """Safely render HTML content directly to the DOM without markdown code block parsing."""
    clean = textwrap.dedent(html_content).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)


def inject_custom_css() -> None:
    """Inject custom styles into Streamlit without breaking core widgets."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            render_html(f"<style>{css_content}</style>")
    else:
        # Fallback inline basic rules
        render_html(
            f"""
            <style>
                .stApp {{
                    background-color: {UIThemeConfig.BG_DARK};
                    color: {UIThemeConfig.TEXT_PRIMARY};
                }}
            </style>
            """
        )


def render_app_header(dataset_name: str | None = None, row_count: int = 0) -> None:
    """Render top application brand banner with live dataset status badge."""
    inject_custom_css()

    if dataset_name:
        status_html = (
            '<div class="header-status-badge">'
            '<span class="badge-pill badge-success">● Active Dataset</span>'
            f'<div style="font-size: 0.85rem; font-weight: 600; color: #F9FAFB; margin-top: 4px;">{dataset_name}</div>'
            f'<div style="font-size: 0.75rem; color: #9CA3AF;">{row_count:,} records loaded</div>'
            '</div>'
        )
    else:
        status_html = (
            '<div class="header-status-badge">'
            '<span class="badge-pill badge-warning">○ No Dataset Loaded</span>'
            '<div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 4px;">Upload data or select sample</div>'
            '</div>'
        )

    header_html = (
        '<div class="app-header-container">'
        '<div class="brand-header-left">'
        f'<h1 class="brand-title">{AppConfig.APP_NAME}</h1>'
        f'<p class="brand-tagline">{AppConfig.TAGLINE}</p>'
        '</div>'
        f'{status_html}'
        '</div>'
    )
    render_html(header_html)


def render_app_footer() -> None:
    """Render professional footer with attribution, privacy assurance, and phase info."""
    footer_html = (
        '<div class="app-footer">'
        '<div>'
        f'<strong>{AppConfig.APP_NAME}</strong> v{AppConfig.VERSION} &nbsp;•&nbsp; '
        f'<span>{AppConfig.TAGLINE}</span>'
        '</div>'
        '<div>'
        '<span>🔒 Local In-Memory Processing &nbsp;•&nbsp; No Data Transmitted to External APIs</span>'
        '</div>'
        '</div>'
    )
    render_html(footer_html)
