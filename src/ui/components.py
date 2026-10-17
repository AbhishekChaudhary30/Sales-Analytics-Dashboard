"""Reusable visual components: metric cards, step indicators, and alerts."""



from src.config import UIThemeConfig
from src.ui.layout import render_html


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
            f'<div class="step-item {state_class}">'
            f'<div class="step-badge">{icon}</div>'
            f'<span>{name}</span>'
            '</div>'
        )

    arrow_divider = '<div style="color: rgba(255,255,255,0.2);">→</div>'
    full_html = (
        '<div class="step-indicator-bar">'
        f'{arrow_divider.join(html_items)}'
        '</div>'
    )
    render_html(full_html)


def render_metric_card(
    label: str,
    value: str,
    sublabel: str | None = None,
    icon: str = "📊",
    color: str = UIThemeConfig.PRIMARY_VIOLET,
) -> None:
    """Render a modern glassmorphic metric card with custom icon and sublabel."""
    sublabel_html = f'<div class="metric-sublabel">{sublabel}</div>' if sublabel else ""
    card_html = (
        f'<div class="metric-card" style="border-left: 4px solid {color};">'
        '<div class="metric-header">'
        f'<span class="metric-label">{label}</span>'
        f'<span class="metric-icon">{icon}</span>'
        '</div>'
        f'<div class="metric-value">{value}</div>'
        f'{sublabel_html}'
        '</div>'
    )
    render_html(card_html)


def render_section_heading(title: str, subtitle: str | None = None, icon: str = "🔹") -> None:
    """Render uniform section heading with border accent."""
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    html = (
        '<div class="section-heading-box">'
        f'<h3 class="section-title">{icon} {title}</h3>'
        f'{sub_html}'
        '</div>'
    )
    render_html(html)


def render_empty_state(
    title: str = "No Data Available",
    description: str = "Upload a dataset or load the sample data to begin analysis.",
    icon: str = "📂",
) -> None:
    """Render centered empty state container with explanation."""
    empty_html = (
        '<div style="text-align: center; padding: 3rem 1.5rem; background: rgba(17, 24, 39, 0.4); '
        'border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 14px; margin: 1.5rem 0;">'
        f'<div style="font-size: 3rem; margin-bottom: 0.75rem;">{icon}</div>'
        f'<h4 style="color: #F9FAFB; margin-bottom: 0.5rem;">{title}</h4>'
        f'<p style="color: #9CA3AF; max-width: 480px; margin: 0 auto; font-size: 0.9rem;">{description}</p>'
        '</div>'
    )
    render_html(empty_html)


def render_quality_warnings_box(warnings: list[str]) -> None:
    """Display expandable or highlighted callouts for data quality warnings."""
    if not warnings:
        render_html(
            '<div style="padding: 0.75rem 1rem; border-radius: 8px; background: rgba(16, 185, 129, 0.1); '
            'border: 1px solid rgba(16, 185, 129, 0.25); color: #34D399; font-size: 0.875rem;">'
            '✅ <strong>Data Quality Check Passed:</strong> No structural anomalies or severe missing value thresholds detected.'
            '</div>'
        )
        return

    items_html = "".join([f"<li style='margin-bottom: 4px;'>{w}</li>" for w in warnings])
    render_html(
        f'<div style="padding: 1rem 1.25rem; border-radius: 10px; background: rgba(245, 158, 11, 0.1); '
        f'border: 1px solid rgba(245, 158, 11, 0.3); color: #FBBF24; font-size: 0.875rem; margin-bottom: 1rem;">'
        f'<strong>⚠️ Data Quality Notes ({len(warnings)} detected):</strong>'
        f'<ul style="margin: 0.5rem 0 0 1.2rem; padding: 0;">{items_html}</ul>'
        '</div>'
    )
