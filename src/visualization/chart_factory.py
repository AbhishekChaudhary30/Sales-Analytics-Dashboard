"""Reusable Plotly chart factory for consistent, polished business visual reports."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import UIThemeConfig
from src.visualization.themes import apply_theme_to_figure


def create_empty_state_figure(message: str = "No data available for this chart") -> go.Figure:
    """Return an empty placeholder figure with a clean centered message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color=UIThemeConfig.TEXT_MUTED),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_theme_to_figure(fig)


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: str | None = None,
    orientation: str = "v",
    barmode: str = "relative",
) -> go.Figure:
    """Create a styled bar chart with clean hover styling."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Bar Chart'}")

    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color_col,
        orientation=orientation,
        barmode=barmode,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(
        marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
        hoverlabel=dict(bgcolor=UIThemeConfig.BG_CARD_ELEVATED),
    )
    return apply_theme_to_figure(fig)


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: str | None = None,
    markers: bool = True,
) -> go.Figure:
    """Create a styled line chart for time-series and trend tracking."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Line Chart'}")

    fig = px.line(
        df,
        x=x,
        y=y,
        color=color_col,
        markers=markers,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=6),
    )
    return apply_theme_to_figure(fig)


def create_area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: str | None = None,
) -> go.Figure:
    """Create a smooth area chart for volume and cumulative revenue trends."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Area Chart'}")

    fig = px.area(
        df,
        x=x,
        y=y,
        color=color_col,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    return apply_theme_to_figure(fig)


def create_donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str = "",
    hole: float = 0.6,
) -> go.Figure:
    """Create a sleek donut chart with high-contrast text and hover info."""
    if df.empty or names not in df.columns or values not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Donut Chart'}")

    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=hole,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        marker=dict(line=dict(color=UIThemeConfig.BG_CARD, width=2)),
    )
    return apply_theme_to_figure(fig)


def create_histogram(
    df: pd.DataFrame,
    x: str,
    title: str = "",
    nbins: int = 25,
) -> go.Figure:
    """Create a distribution histogram for order value, quantities, or discounts."""
    if df.empty or x not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Histogram'}")

    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        title=title,
        color_discrete_sequence=[UIThemeConfig.PRIMARY_VIOLET],
    )
    fig.update_traces(
        marker=dict(line=dict(color="rgba(255,255,255,0.2)", width=1)),
        opacity=0.85,
    )
    return apply_theme_to_figure(fig)


def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    size_col: str | None = None,
    color_col: str | None = None,
    hover_name: str | None = None,
) -> go.Figure:
    """Create a 2D scatter or bubble chart (e.g. Sales vs Profit by Discount)."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Scatter Chart'}")

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size_col,
        color=color_col,
        hover_name=hover_name,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="white")))
    return apply_theme_to_figure(fig)


def create_box_plot(
    df: pd.DataFrame,
    x: str | None = None,
    y: str | None = None,
    title: str = "",
) -> go.Figure:
    """Create box plots for spread and outlier detection."""
    if df.empty:
        return create_empty_state_figure(f"Data not available for {title or 'Box Plot'}")

    fig = px.box(
        df,
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=[UIThemeConfig.SECONDARY_CYAN],
    )
    return apply_theme_to_figure(fig)


def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str = "",
) -> go.Figure:
    """Create a correlation or pivot matrix heatmap."""
    if df.empty:
        return create_empty_state_figure(f"Data not available for {title or 'Heatmap'}")

    fig = px.density_heatmap(
        df,
        x=x,
        y=y,
        z=z,
        title=title,
        color_continuous_scale=[
            [0.0, "#0B0F19"],
            [0.5, "#06B6D4"],
            [1.0, "#8B5CF6"],
        ],
    )
    return apply_theme_to_figure(fig)
