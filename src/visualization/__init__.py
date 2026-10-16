"""Visualization module providing Plotly themes, chart factory, and interactive chart explorer."""

from src.visualization.chart_factory import (
    create_3d_scatter,
    create_area_chart,
    create_bar_chart,
    create_box_plot,
    create_choropleth_map,
    create_correlation_heatmap,
    create_donut_chart,
    create_empty_state_figure,
    create_funnel_chart,
    create_heatmap,
    create_histogram,
    create_horizontal_bar_chart,
    create_line_chart,
    create_scatter_chart,
    create_treemap,
    create_waterfall_chart,
)
from src.visualization.explorer import render_chart_explorer
from src.visualization.themes import apply_theme_to_figure, get_dashboard_plotly_template

__all__ = [
    "apply_theme_to_figure",
    "create_3d_scatter",
    "create_area_chart",
    "create_bar_chart",
    "create_box_plot",
    "create_choropleth_map",
    "create_correlation_heatmap",
    "create_donut_chart",
    "create_empty_state_figure",
    "create_funnel_chart",
    "create_heatmap",
    "create_histogram",
    "create_horizontal_bar_chart",
    "create_line_chart",
    "create_scatter_chart",
    "create_treemap",
    "create_waterfall_chart",
    "get_dashboard_plotly_template",
    "render_chart_explorer",
]
