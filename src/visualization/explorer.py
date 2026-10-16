"""Interactive Chart Explorer component allowing users to construct ad-hoc Plotly visualizations."""

import pandas as pd
import streamlit as st

from src.visualization.chart_factory import (
    create_3d_scatter,
    create_area_chart,
    create_bar_chart,
    create_box_plot,
    create_donut_chart,
    create_heatmap,
    create_horizontal_bar_chart,
    create_line_chart,
    create_scatter_chart,
    create_treemap,
)


def render_chart_explorer(df: pd.DataFrame) -> None:
    """Render the self-service Interactive Chart Explorer."""
    if df.empty:
        st.info("Please load or filter a dataset to construct custom visualizations.")
        return

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    all_cols = list(df.columns)

    chart_types = [
        "Vertical Bar Chart",
        "Horizontal Bar Chart",
        "Line Chart",
        "Area Chart",
        "Donut Chart",
        "Scatter / Bubble Plot",
        "Box Plot",
        "Treemap",
        "Heatmap",
        "3D Scatter Plot",
    ]

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

    with col_ctrl1:
        selected_chart = st.selectbox("Select Chart Type", chart_types, key="ce_chart_type")

    with col_ctrl2:
        x_col = st.selectbox(
            "X-Axis / Category Dimension",
            all_cols,
            index=0 if all_cols else None,
            key="ce_x_axis",
        )

    with col_ctrl3:
        y_default = 0
        if "sales" in numeric_cols:
            y_default = numeric_cols.index("sales")
        y_col = st.selectbox(
            "Y-Axis / Primary Measure",
            numeric_cols if numeric_cols else all_cols,
            index=y_default if numeric_cols else 0,
            key="ce_y_axis",
        )

    # Secondary configuration row
    c_sub1, c_sub2, c_sub3 = st.columns(3)

    with c_sub1:
        agg_method = st.selectbox("Aggregation Method", ["Sum", "Mean (Average)", "Count", "Max", "Min"], key="ce_agg_method")

    with c_sub2:
        color_candidates = ["None"] + all_cols
        color_col_sel = st.selectbox("Color / Group Dimension (Optional)", color_candidates, key="ce_color_col")
        color_col = None if color_col_sel == "None" else color_col_sel

    with c_sub3:
        top_n = st.slider("Top N Limit", min_value=5, max_value=min(50, len(df)), value=15, step=5, key="ce_top_n")

    # Validation and Chart Generation
    st.markdown("---")

    agg_func_map = {
        "Sum": "sum",
        "Mean (Average)": "mean",
        "Count": "count",
        "Max": "max",
        "Min": "min",
    }
    agg_fn = agg_func_map[agg_method]

    fig = None
    try:
        if selected_chart in ["Vertical Bar Chart", "Horizontal Bar Chart"]:
            # Aggregate by x_col
            valid_df = df.dropna(subset=[x_col, y_col]).copy()
            valid_df[y_col] = pd.to_numeric(valid_df[y_col], errors="coerce")
            agg_df = valid_df.groupby(x_col)[y_col].agg(agg_fn).reset_index().sort_values(by=y_col, ascending=False).head(top_n)

            if selected_chart == "Vertical Bar Chart":
                fig = create_bar_chart(agg_df, x=x_col, y=y_col, title=f"{y_col.title()} by {x_col.title()} ({agg_method})")
            else:
                fig = create_horizontal_bar_chart(agg_df, x=y_col, y=x_col, title=f"{y_col.title()} by {x_col.title()} ({agg_method})")

        elif selected_chart == "Line Chart":
            valid_df = df.dropna(subset=[x_col, y_col]).copy()
            valid_df[y_col] = pd.to_numeric(valid_df[y_col], errors="coerce")
            agg_df = valid_df.groupby(x_col)[y_col].agg(agg_fn).reset_index().sort_values(by=x_col)
            fig = create_line_chart(agg_df, x=x_col, y=y_col, title=f"{y_col.title()} Trend across {x_col.title()}")

        elif selected_chart == "Area Chart":
            valid_df = df.dropna(subset=[x_col, y_col]).copy()
            valid_df[y_col] = pd.to_numeric(valid_df[y_col], errors="coerce")
            agg_df = valid_df.groupby(x_col)[y_col].agg(agg_fn).reset_index().sort_values(by=x_col)
            fig = create_area_chart(agg_df, x=x_col, y=y_col, title=f"{y_col.title()} Cumulative by {x_col.title()}")

        elif selected_chart == "Donut Chart":
            valid_df = df.dropna(subset=[x_col, y_col]).copy()
            valid_df[y_col] = pd.to_numeric(valid_df[y_col], errors="coerce")
            agg_df = valid_df.groupby(x_col)[y_col].agg(agg_fn).reset_index().sort_values(by=y_col, ascending=False).head(top_n)
            fig = create_donut_chart(agg_df, names=x_col, values=y_col, title=f"{y_col.title()} Breakdown by {x_col.title()}")

        elif selected_chart == "Scatter / Bubble Plot":
            if not pd.api.types.is_numeric_dtype(df[x_col]):
                st.warning(f"⚠️ Scatter plots require a numeric X-Axis. '{x_col}' is categorical. Choose a numeric column or bar chart.")
                return
            fig = create_scatter_chart(df, x=x_col, y=y_col, color_col=color_col, title=f"{x_col.title()} vs {y_col.title()}")

        elif selected_chart == "Box Plot":
            fig = create_box_plot(df, x=x_col, y=y_col, title=f"Distribution of {y_col.title()} across {x_col.title()}")

        elif selected_chart == "Treemap":
            path_candidates = [c for c in [x_col, color_col] if c and c in df.columns]
            if not path_candidates:
                path_candidates = [x_col]
            fig = create_treemap(df, path=path_candidates, values=y_col, title=f"{y_col.title()} Hierarchical Treemap")

        elif selected_chart == "Heatmap":
            if not color_col:
                st.info("💡 To construct a 2D Heatmap, please select a secondary 'Color / Group Dimension' in the dropdown above to serve as the vertical axis.")
                return
            fig = create_heatmap(
                df,
                x=x_col,
                y=color_col,
                values=y_col,
                aggfunc=agg_fn,
                title=f"{y_col.title()} Heatmap across {x_col.title()} & {color_col.title()} ({agg_method})",
            )

        elif selected_chart == "3D Scatter Plot":
            if len(numeric_cols) < 3:
                st.warning("⚠️ 3D Scatter plot requires at least 3 numeric dimensions in the dataset.")
                return
            z_candidates = [c for c in numeric_cols if c not in (x_col, y_col)]
            z_col = z_candidates[0] if z_candidates else numeric_cols[0]
            fig = create_3d_scatter(df, x=x_col, y=y_col, z=z_col, color_col=color_col, title=f"3D: {x_col} × {y_col} × {z_col}")

        if fig:
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Could not render {selected_chart}: {str(e)}")
