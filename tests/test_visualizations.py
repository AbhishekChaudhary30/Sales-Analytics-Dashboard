import pandas as pd
import plotly.graph_objects as go
import pytest

from src.visualization import (
    apply_theme_to_figure,
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
    get_dashboard_plotly_template,
    render_chart_explorer,
)


@pytest.fixture
def sample_sales_df():
    return pd.DataFrame(
        {
            "category": ["Technology", "Technology", "Furniture", "Furniture", "Office Supplies"],
            "region": ["West", "East", "West", "East", "Central"],
            "sales": [1200.50, 850.00, 420.00, 310.00, 150.00],
            "profit": [320.00, 180.00, -50.00, 20.00, 45.00],
            "quantity": [4, 3, 2, 1, 5],
        }
    )


def test_create_heatmap_with_dimensions(sample_sales_df):
    """Test creating a 2D pivoted heatmap from tabular categorical and numeric columns."""
    fig = create_heatmap(
        sample_sales_df,
        x="category",
        y="region",
        values="sales",
        aggfunc="sum",
        title="Sales by Category & Region",
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
    assert fig.layout.title.text == "Sales by Category & Region"
    assert fig.data[0].z is not None


def test_create_heatmap_with_matrix():
    """Test creating a heatmap directly from a 2D numerical matrix / correlation DataFrame."""
    matrix_df = pd.DataFrame(
        [[1.0, 0.45, -0.2], [0.45, 1.0, 0.15], [-0.2, 0.15, 1.0]],
        columns=["sales", "profit", "discount"],
        index=["sales", "profit", "discount"],
    )
    fig = create_heatmap(matrix_df, title="Direct Correlation Matrix Heatmap")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"
    assert list(fig.data[0].x) == ["sales", "profit", "discount"]
    assert list(fig.data[0].y) == ["sales", "profit", "discount"]


def test_create_heatmap_empty_dataframe():
    """Test that create_heatmap gracefully handles an empty DataFrame."""
    fig = create_heatmap(pd.DataFrame(), title="Empty Heatmap")
    assert isinstance(fig, go.Figure)
    # Empty state figure contains text annotation and hidden axes
    assert len(fig.layout.annotations) > 0
    assert "not available" in fig.layout.annotations[0].text.lower()


def test_create_heatmap_missing_columns(sample_sales_df):
    """Test that create_heatmap handles non-existent column names without crashing."""
    fig = create_heatmap(
        sample_sales_df,
        x="nonexistent_x",
        y="nonexistent_y",
        values="sales",
        title="Missing Column Test",
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0
    assert "not found" in fig.layout.annotations[0].text.lower()


def test_create_heatmap_insufficient_numeric():
    """Test that create_heatmap handles matrices without any numeric columns."""
    text_df = pd.DataFrame(
        {
            "col_a": ["alpha", "beta", "gamma"],
            "col_b": ["delta", "epsilon", "zeta"],
        }
    )
    fig = create_heatmap(text_df, title="Text Only Heatmap")
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.annotations) > 0
    assert "no numeric values" in fig.layout.annotations[0].text.lower()


def test_all_chart_factory_exports(sample_sales_df):
    """Verify that every exported chart factory builder compiles and produces a valid Figure."""
    fig_bar = create_bar_chart(sample_sales_df, x="category", y="sales")
    assert isinstance(fig_bar, go.Figure)

    fig_hbar = create_horizontal_bar_chart(sample_sales_df, x="sales", y="category")
    assert isinstance(fig_hbar, go.Figure)

    fig_line = create_line_chart(sample_sales_df, x="category", y="sales")
    assert isinstance(fig_line, go.Figure)

    fig_area = create_area_chart(sample_sales_df, x="category", y="sales")
    assert isinstance(fig_area, go.Figure)

    fig_donut = create_donut_chart(sample_sales_df, names="category", values="sales")
    assert isinstance(fig_donut, go.Figure)

    fig_scatter = create_scatter_chart(sample_sales_df, x="sales", y="profit")
    assert isinstance(fig_scatter, go.Figure)

    fig_box = create_box_plot(sample_sales_df, x="category", y="sales")
    assert isinstance(fig_box, go.Figure)

    fig_hist = create_histogram(sample_sales_df, x="sales")
    assert isinstance(fig_hist, go.Figure)

    fig_tree = create_treemap(sample_sales_df, path=["region", "category"], values="sales")
    assert isinstance(fig_tree, go.Figure)

    fig_waterfall = create_waterfall_chart(["Gross", "Returns", "Net"], [1000, -200, 800])
    assert isinstance(fig_waterfall, go.Figure)

    fig_funnel = create_funnel_chart(["Stage 1", "Stage 2"], [100, 50])
    assert isinstance(fig_funnel, go.Figure)

    fig_3d = create_3d_scatter(sample_sales_df, x="sales", y="profit", z="quantity")
    assert isinstance(fig_3d, go.Figure)

    fig_empty = create_empty_state_figure("Custom Empty Notice")
    assert isinstance(fig_empty, go.Figure)

    corr_df = sample_sales_df[["sales", "profit", "quantity"]].corr()
    fig_corr = create_correlation_heatmap(corr_df)
    assert isinstance(fig_corr, go.Figure)

    fig_map = create_choropleth_map(
        pd.DataFrame({"state": ["CA", "NY"], "sales": [1000, 500]}),
        locations_col="state",
        values_col="sales",
    )
    assert isinstance(fig_map, go.Figure)

    template = get_dashboard_plotly_template()
    assert template is not None

    fig_themed = apply_theme_to_figure(go.Figure())
    assert isinstance(fig_themed, go.Figure)

    assert callable(render_chart_explorer)
