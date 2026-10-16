"""Visualization module providing Plotly themes and chart factory."""

from src.visualization.chart_factory import (
    create_area_chart,
    create_bar_chart,
    create_box_plot,
    create_donut_chart,
    create_heatmap,
    create_histogram,
    create_line_chart,
    create_scatter_chart,
)
from src.visualization.themes import (
    apply_theme_to_figure,
    get_dashboard_plotly_template,
)

__all__ = [
    "apply_theme_to_figure",
    "create_area_chart",
    "create_bar_chart",
    "create_box_plot",
    "create_donut_chart",
    "create_heatmap",
    "create_histogram",
    "create_line_chart",
    "create_scatter_chart",
    "get_dashboard_plotly_template",
]
