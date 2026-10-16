"""Custom Plotly theme configured for dark graphite, electric violet, and cyan."""

import plotly.graph_objects as go
import plotly.io as pio

from src.config import UIThemeConfig

THEME_NAME = "sales_dark_graphite"


def get_dashboard_plotly_template() -> go.layout.Template:
    """Build and register custom Plotly template for consistent dashboard charts."""
    template = go.layout.Template()

    # Layout styling
    template.layout = go.Layout(
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=12,
            color=UIThemeConfig.TEXT_SECONDARY,
        ),
        title=dict(
            font=dict(
                family="Inter, -apple-system, sans-serif",
                size=16,
                color=UIThemeConfig.TEXT_PRIMARY,
            ),
            x=0.02,
            xanchor="left",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17, 24, 39, 0.4)",
        colorway=list(UIThemeConfig.PLOTLY_PALETTE),
        hoverlabel=dict(
            bgcolor=UIThemeConfig.BG_CARD_ELEVATED,
            bordercolor=UIThemeConfig.PRIMARY_VIOLET,
            font=dict(
                family="Inter, sans-serif",
                size=12,
                color=UIThemeConfig.TEXT_PRIMARY,
            ),
        ),
        margin=dict(l=40, r=30, t=50, b=40),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color=UIThemeConfig.TEXT_MUTED),
            title=dict(font=dict(color=UIThemeConfig.TEXT_SECONDARY)),
            zerolinecolor="rgba(255, 255, 255, 0.1)",
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color=UIThemeConfig.TEXT_MUTED),
            title=dict(font=dict(color=UIThemeConfig.TEXT_SECONDARY)),
            zerolinecolor="rgba(255, 255, 255, 0.1)",
        ),
        legend=dict(
            bgcolor="rgba(17, 24, 39, 0.6)",
            bordercolor=UIThemeConfig.BORDER_DEFAULT,
            font=dict(color=UIThemeConfig.TEXT_SECONDARY),
        ),
    )

    return template


def register_dashboard_theme() -> None:
    """Register theme in Plotly's global templates collection."""
    template = get_dashboard_plotly_template()
    pio.templates[THEME_NAME] = template
    pio.templates.default = THEME_NAME


def apply_theme_to_figure(fig: go.Figure) -> go.Figure:
    """Apply standard layout styling and glassmorphic dark theme to any Plotly figure."""
    fig.update_layout(
        template=get_dashboard_plotly_template(),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17, 24, 39, 0.5)",
    )
    return fig


# Automatically register upon module load
register_dashboard_theme()
