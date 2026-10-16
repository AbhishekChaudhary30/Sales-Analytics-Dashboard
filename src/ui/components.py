"""Reusable visual components: metric cards, step indicators, and alerts."""


import streamlit as st

from src.config import UIThemeConfig


def render_step_indicator(current_step: int) -> None:
    """Render horizontal step indicator showing user journey from Upload to Reports."""
    steps = [
        (1, "Overview"),
        (2, "Upload"),
        (3, "Inspection"),
        (4, "Mapping"),
        (5, "Workspace"),
        (6, "Reports"),
    ]

    html_items = []
    for step_num, name in steps:
        if step_num == current_step:
            state_class = "active"
        elif step_num < current_step:
            state_class = "completed"
        else:
            state_class = "pending"

        icon = "✓" if step_num < current_step else str(step_num)
        html_items.append(
            f"""
            <div class="step-item {state_class}">
                <div class="step-badge">{icon}</div>
                <span>{name}</span>
            </div>
            """
        )

    full_html = f"""
    <div class="step-indicator-bar">
        {'<div style="color: rgba(255,255,255,0.2);">→</div>'.join(html_items)}
    </div>
    """
    st.markdown(full_html, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    sublabel: str | None = None,
    icon: str = "📊",
    color: str = UIThemeConfig.PRIMARY_VIOLET,
) -> None:
    """Render a modern glassmorphic metric card with custom icon and sublabel."""
    sublabel_html = f'<div class="metric-sublabel">{sublabel}</div>' if sublabel else ""
    card_html = f"""
    <div class="metric-card" style="border-left: 4px solid {color};">
        <div class="metric-header">
            <span class="metric-label">{label}</span>
            <span class="metric-icon">{icon}</span>
        </div>
        <div class="metric-value">{value}</div>
        {sublabel_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_section_heading(title: str, subtitle: str | None = None, icon: str = "🔹") -> None:
    """Render uniform section heading with border accent."""
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    html = f"""
    <div class="section-heading-box">
        <h3 class="section-title">{icon} {title}</h3>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(
    title: str = "No Data Available",
    description: str = "Upload a dataset or load the sample data to begin analysis.",
    icon: str = "📂",
) -> None:
    """Render centered empty state container with explanation."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem 1.5rem; background: rgba(17, 24, 39, 0.4);
                    border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 14px; margin: 1.5rem 0;">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">{icon}</div>
            <h4 style="color: #F9FAFB; margin-bottom: 0.5rem;">{title}</h4>
            <p style="color: #9CA3AF; max-width: 480px; margin: 0 auto; font-size: 0.9rem;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quality_warnings_box(warnings: list[str]) -> None:
    """Display expandable or highlighted callouts for data quality warnings."""
    if not warnings:
        st.markdown(
            """
            <div style="padding: 0.75rem 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.1);
                        border: 1px solid rgba(16, 185, 129, 0.25); color: #34D399; font-size: 0.875rem;">
                ✅ <strong>Data Quality Check Passed:</strong> No structural anomalies or severe missing value thresholds detected.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    items_html = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in warnings])
    st.markdown(
        f"""
        <div style="padding: 1rem 1.25rem; border-radius: 10px; background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.3); color: #FBBF24; font-size: 0.875rem; margin-bottom: 1rem;">
            <strong>⚠️ Data Quality Notes ({len(warnings)} detected):</strong>
            <ul style="margin: 0.5rem 0 0 1.2rem; padding: 0;">
                {items_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
