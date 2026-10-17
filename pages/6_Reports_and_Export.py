"""Step 6: Reports & Filtered Data Export Center."""

import pandas as pd
import streamlit as st

from src.analytics.insights import generate_comprehensive_insights
from src.analytics.metrics import compute_all_kpis
from src.analytics.products import analyze_categories
from src.ui.components import (
    render_empty_state,
    render_section_heading,
    render_step_indicator,
)
from src.ui.layout import render_app_footer, render_app_header, render_html
from src.ui.navigation import (
    get_current_dataset,
    has_active_dataset,
    init_session_state,
    render_step_navigation,
)

init_session_state()

active_ds = get_current_dataset()
ds_name = active_ds.file_name if active_ds else None
ds_rows = active_ds.total_rows if active_ds else 0

render_app_header(dataset_name=ds_name, row_count=ds_rows)
render_step_indicator(current_step=6)

render_section_heading(
    title="Reports & Analytical Data Export",
    subtitle="Download filtered datasets, dimensional rollups, KPI summaries, and structured insights.",
    icon="📑",
)

if not has_active_dataset():
    render_empty_state(
        title="No Data Available for Export",
        description="Please load or upload a sales dataset in Step 1 or 2 first.",
        icon="📂",
    )
    render_step_navigation(
        current_step=6,
        prev_page="pages/5_Analysis_Workspace.py",
        next_page=None,
        can_advance=False,
    )
    render_app_footer()
    st.stop()

# Retrieve active filtered or standardized dataset
filtered_df = st.session_state.get("filtered_df")
standard_df = st.session_state.get("standard_df")
target_df = filtered_df if filtered_df is not None else (standard_df if standard_df is not None else active_ds.raw_df)

if target_df.empty:
    st.warning("⚠️ The current filter selection contains 0 rows. Download options are disabled.")
    render_step_navigation(current_step=6, prev_page="pages/5_Analysis_Workspace.py", next_page="pages/1_Overview.py")
    render_app_footer()
    st.stop()

scope_html = (
    '<div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25); '
    'border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">'
    '<span class="badge-pill badge-info">Active Filter Scope</span>'
    '<div style="font-size: 0.95rem; font-weight: 600; color: #F9FAFB; margin-top: 4px;">'
    f'Exporting {len(target_df):,} transaction records (Filtered working copy)'
    '</div>'
    '</div>'
)
render_html(scope_html)

st.markdown("#### Available Commercial Exports")

c1, c2 = st.columns(2)

with c1:
    # 1. Standardized Filtered CSV
    card1_html = (
        '<div class="metric-card" style="border-left: 4px solid #8B5CF6; min-height: 180px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Processed Dataset</span>'
        '<span class="metric-icon">📥</span>'
        '</div>'
        '<div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.35rem;">'
        'Filtered Transactions CSV'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">'
        'Full line-item transaction dataset reflecting active date, category, and regional filters.'
        '</p>'
        '</div>'
    )
    render_html(card1_html)
    csv_bytes = target_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered CSV",
        data=csv_bytes,
        file_name="filtered_sales_transactions.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )

with c2:
    # 2. Executive KPI Summary CSV
    card2_html = (
        '<div class="metric-card" style="border-left: 4px solid #06B6D4; min-height: 180px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Executive Metrics</span>'
        '<span class="metric-icon">📊</span>'
        '</div>'
        '<div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.35rem;">'
        'Executive KPI Summary Table'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">'
        'Consolidated table of high-level financial indicators, unit sales, margins, and definitions.'
        '</p>'
        '</div>'
    )
    render_html(card2_html)
    kpis = compute_all_kpis(target_df)
    kpi_records = [
        {
            "Indicator": m.display_name,
            "Value": m.formatted_value,
            "Numerical Value": m.value,
            "Availability": "Available" if m.is_available else "Unavailable",
            "Definition": m.definition,
        }
        for m in kpis.kpi_dict.values()
    ]
    kpi_df = pd.DataFrame(kpi_records)
    kpi_csv_bytes = kpi_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download KPI Summary CSV",
        data=kpi_csv_bytes,
        file_name="executive_kpi_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )

render_html("<div style='height: 0.75rem;'></div>")
c3, c4 = st.columns(2)

with c3:
    # 3. Category Rollup Summary
    card3_html = (
        '<div class="metric-card" style="border-left: 4px solid #10B981; min-height: 180px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Assortment Rollup</span>'
        '<span class="metric-icon">📦</span>'
        '</div>'
        '<div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.35rem;">'
        'Category Performance Summary'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">'
        'Aggregated category revenues, net margins, revenue shares, and total unit counts.'
        '</p>'
        '</div>'
    )
    render_html(card3_html)
    if "category" in target_df.columns:
        cat_summary_df = analyze_categories(target_df)
        cat_csv = cat_summary_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Category Summary CSV",
            data=cat_csv,
            file_name="category_performance_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("Category field unmapped.")

with c4:
    # 4. Automated Insights Briefing (Markdown Report)
    card4_html = (
        '<div class="metric-card" style="border-left: 4px solid #F59E0B; min-height: 180px;">'
        '<div class="metric-header">'
        '<span class="metric-label">Intelligence Brief</span>'
        '<span class="metric-icon">💡</span>'
        '</div>'
        '<div style="font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin-bottom: 0.35rem;">'
        'Automated Insights Executive Brief'
        '</div>'
        '<p style="color: #9CA3AF; font-size: 0.8rem; line-height: 1.4; margin-bottom: 1rem;">'
        'Structured markdown briefing documenting all quantified commercial observations and recommendations.'
        '</p>'
        '</div>'
    )
    render_html(card4_html)
    insights = generate_comprehensive_insights(target_df)
    report_lines = [
        "# Sales Analytics Dashboard - Executive Intelligence Brief\n",
        f"**Active Records Analyzed**: {len(target_df):,}\n",
        "## Key Automated Business Findings\n",
    ]
    for ins in insights:
        report_lines.append(f"### {ins.icon} {ins.title}")
        report_lines.append(f"- **Finding**: {ins.description}")
        report_lines.append(f"- **Observed Value**: {ins.observed_value}")
        if ins.recommendation:
            report_lines.append(f"- **Strategic Recommendation**: {ins.recommendation}")
        report_lines.append("")

    report_text = "\n".join(report_lines)
    st.download_button(
        label="Download Insights Brief (Markdown)",
        data=report_text.encode("utf-8"),
        file_name="sales_executive_insights_brief.md",
        mime="text/markdown",
        use_container_width=True,
    )

# Bottom Navigation
render_step_navigation(
    current_step=6,
    prev_page="pages/5_Analysis_Workspace.py",
    next_page="pages/1_Overview.py",
    next_label="Return to Overview 🏠",
    can_advance=True,
)

render_app_footer()
