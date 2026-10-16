"""Expanded Plotly Chart Factory supporting 15+ interactive chart varieties."""

from typing import List, Optional

import numpy as np
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
    color_col: Optional[str] = None,
    orientation: str = "v",
    barmode: str = "relative",
    top_n: Optional[int] = None,
) -> go.Figure:
    """Create a styled vertical or horizontal bar chart."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Bar Chart'}")

    plot_df = df.head(top_n) if top_n else df

    fig = px.bar(
        plot_df,
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


def create_horizontal_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: Optional[str] = None,
    top_n: Optional[int] = None,
) -> go.Figure:
    """Create horizontal bar chart optimal for displaying long product or entity names."""
    if df.empty or x not in df.columns or y not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Horizontal Bar Chart'}")

    plot_df = df.head(top_n) if top_n else df
    # Reverse order so top item appears at top of horizontal chart
    plot_df = plot_df.iloc[::-1]

    fig = px.bar(
        plot_df,
        x=x,
        y=y,
        color=color_col,
        orientation="h",
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    return apply_theme_to_figure(fig)


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: Optional[str] = None,
    secondary_y_col: Optional[str] = None,
    markers: bool = True,
) -> go.Figure:
    """Create a styled line chart with optional secondary trend or moving average trace."""
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
    fig.update_traces(line=dict(width=2.5), marker=dict(size=6))

    if secondary_y_col and secondary_y_col in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df[x],
                y=df[secondary_y_col],
                mode="lines",
                name=secondary_y_col.replace("_", " ").title(),
                line=dict(dash="dot", width=2, color=UIThemeConfig.COLOR_WARNING),
            )
        )

    return apply_theme_to_figure(fig)


def create_area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color_col: Optional[str] = None,
) -> go.Figure:
    """Create smooth area chart for volume and cumulative revenue trends."""
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
    """Create a high-contrast donut chart."""
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


def create_treemap(
    df: pd.DataFrame,
    path: List[str],
    values: str,
    title: str = "",
) -> go.Figure:
    """Create hierarchical treemap (e.g. Category -> Subcategory -> Product)."""
    valid_path = [p for p in path if p in df.columns]
    if df.empty or not valid_path or values not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Treemap'}")

    clean_df = df.dropna(subset=valid_path + [values]).copy()
    clean_df[values] = pd.to_numeric(clean_df[values], errors="coerce").fillna(0)
    clean_df = clean_df[clean_df[values] > 0]

    if clean_df.empty:
        return create_empty_state_figure(f"No positive values for {title or 'Treemap'}")

    fig = px.treemap(
        clean_df,
        path=valid_path,
        values=values,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(marker=dict(cornerradius=4))
    return apply_theme_to_figure(fig)


def create_waterfall_chart(
    labels: List[str],
    values: List[float],
    title: str = "Revenue & Margin Bridge",
) -> go.Figure:
    """Create a waterfall bridge chart illustrating progression from Gross Revenue to Net Margin."""
    if not labels or not values or len(labels) != len(values):
        return create_empty_state_figure("Insufficient data for Waterfall chart")

    measures = ["relative"] * (len(values) - 1) + ["total"]

    fig = go.Figure(
        go.Waterfall(
            name="Bridge",
            orientation="v",
            measure=measures,
            x=labels,
            y=values,
            textposition="outside",
            text=[f"{v:+,.0f}" if i < len(values) - 1 else f"{v:,.0f}" for i, v in enumerate(values)],
            connector=dict(line=dict(color="rgba(255,255,255,0.2)")),
            increasing=dict(marker=dict(color=UIThemeConfig.COLOR_SUCCESS)),
            decreasing=dict(marker=dict(color=UIThemeConfig.COLOR_DANGER)),
            totals=dict(marker=dict(color=UIThemeConfig.PRIMARY_VIOLET)),
        )
    )
    fig.update_layout(title=title)
    return apply_theme_to_figure(fig)


def create_funnel_chart(
    stages: List[str],
    values: List[float],
    title: str = "Sales Pipeline Funnel",
) -> go.Figure:
    """Create funnel visualization for progressive process stages."""
    if not stages or not values or len(stages) != len(values):
        return create_empty_state_figure("Insufficient data for Funnel chart")

    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=list(UIThemeConfig.PLOTLY_PALETTE)[: len(stages)],
                line=dict(width=1, color="rgba(255,255,255,0.2)"),
            ),
        )
    )
    fig.update_layout(title=title)
    return apply_theme_to_figure(fig)


def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    size_col: Optional[str] = None,
    color_col: Optional[str] = None,
    hover_name: Optional[str] = None,
) -> go.Figure:
    """Create 2D scatter or bubble chart with hover tooltips."""
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


def create_3d_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    color_col: Optional[str] = None,
    title: str = "3D Multi-Dimensional Scatter Plot",
) -> go.Figure:
    """Create a 3D scatter plot when at least three meaningful numeric dimensions exist."""
    req_cols = [x, y, z]
    if df.empty or any(c not in df.columns for c in req_cols):
        return create_empty_state_figure("3D Scatter requires three valid columns")

    fig = px.scatter_3d(
        df,
        x=x,
        y=y,
        z=z,
        color=color_col,
        title=title,
        color_discrete_sequence=list(UIThemeConfig.PLOTLY_PALETTE),
    )
    fig.update_traces(marker=dict(size=4, opacity=0.8))
    return apply_theme_to_figure(fig)


def create_correlation_heatmap(corr_df: pd.DataFrame, title: str = "Metric Correlation Matrix") -> go.Figure:
    """Create annotated heatmap representing Pearson/Spearman correlation coefficients."""
    if corr_df.empty:
        return create_empty_state_figure("Insufficient numeric columns for correlation matrix")

    fig = go.Figure(
        data=go.Heatmap(
            z=corr_df.values,
            x=list(corr_df.columns),
            y=list(corr_df.index),
            colorscale=[
                [0.0, UIThemeConfig.COLOR_DANGER],
                [0.5, UIThemeConfig.BG_CARD],
                [1.0, UIThemeConfig.COLOR_SUCCESS],
            ],
            zmin=-1.0,
            zmax=1.0,
            text=np.round(corr_df.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
            hoverongaps=False,
        )
    )
    fig.update_layout(title=title)
    return apply_theme_to_figure(fig)


def create_histogram(
    df: pd.DataFrame,
    x: str,
    title: str = "",
    nbins: int = 25,
) -> go.Figure:
    """Create distribution histogram."""
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


def create_box_plot(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: str = "",
) -> go.Figure:
    """Create box plots for outlier and spread inspection."""
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


def create_choropleth_map(
    df: pd.DataFrame,
    locations_col: str,
    values_col: str,
    location_mode: str = "USA-states",
    scope: str = "usa",
    title: str = "Geographic Sales Distribution",
) -> go.Figure:
    """Create an interactive regional or state-level choropleth map."""
    if df.empty or locations_col not in df.columns or values_col not in df.columns:
        return create_empty_state_figure(f"Data not available for {title or 'Choropleth Map'}")

    fig = px.choropleth(
        df,
        locations=locations_col,
        locationmode=location_mode,
        color=values_col,
        scope=scope,
        title=title,
        color_continuous_scale=[
            [0.0, UIThemeConfig.BG_CARD],
            [0.5, UIThemeConfig.SECONDARY_CYAN],
            [1.0, UIThemeConfig.PRIMARY_VIOLET],
        ],
    )
    fig.update_layout(
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(17, 24, 39, 0.8)",
            landcolor=UIThemeConfig.BG_CARD_ELEVATED,
        )
    )
    return apply_theme_to_figure(fig)
