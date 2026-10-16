"""Step 4: Column Mapping & Schema Alignment Page."""

import streamlit as st

from src.config import STANDARD_BUSINESS_FIELDS, UIThemeConfig
from src.data.column_mapping import ColumnMapper, create_standard_dataframe
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_section_heading,
    render_step_indicator,
)
from src.ui.layout import render_app_footer, render_app_header
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
render_step_indicator(current_step=4)

render_section_heading(
    title="Business Column Mapping",
    subtitle="Align detected columns with standard business metrics. Ambiguous fields require user confirmation.",
    icon="🧭",
)

if not has_active_dataset():
    render_empty_state(
        title="No Dataset Available for Mapping",
        description="Please upload or select a dataset first.",
        icon="📂",
    )
    render_step_navigation(
        current_step=4,
        prev_page="pages/3_Data_Inspection.py",
        next_page="pages/5_Analysis_Workspace.py",
        can_advance=False,
        blocking_message="Cannot map columns without an uploaded dataset.",
    )
    render_app_footer()
    st.stop()

# Ensure ColumnMapper is initialized
mapper: ColumnMapper = st.session_state.get("column_mapper")
if mapper is None:
    mapper = ColumnMapper(list(active_ds.raw_df.columns))
    st.session_state["column_mapper"] = mapper

raw_cols = ["(Not Available / Unmapped)"] + list(active_ds.raw_df.columns)

# Overview metrics
mapped_count = mapper.get_mapped_count()
total_std_fields = len(STANDARD_BUSINESS_FIELDS)
is_essential_ok, missing_essentials = mapper.get_essential_status()

c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card(
        label="Mapped Fields",
        value=f"{mapped_count} / {total_std_fields}",
        sublabel="Standard business attributes aligned",
        icon="🔗",
        color=UIThemeConfig.PRIMARY_VIOLET,
    )
with c2:
    status_label = "Essential Fields Ready" if is_essential_ok else "Missing Essential Fields"
    status_color = UIThemeConfig.COLOR_SUCCESS if is_essential_ok else UIThemeConfig.COLOR_DANGER
    render_metric_card(
        label="Readiness Check",
        value="Ready" if is_essential_ok else "Action Required",
        sublabel=status_label,
        icon="🎯",
        color=status_color,
    )
with c3:
    ambig_count = len(mapper.auto_result.ambiguous_fields)
    ambig_color = UIThemeConfig.COLOR_WARNING if ambig_count > 0 else UIThemeConfig.COLOR_SUCCESS
    render_metric_card(
        label="Ambiguous Candidates",
        value=f"{ambig_count}",
        sublabel="Fields requiring manual review",
        icon="⚖️",
        color=ambig_color,
    )

if not is_essential_ok:
    st.warning(
        f"⚠️ **Essential Field Warning**: To compute revenue and time analytics, please map: "
        f"**{', '.join(missing_essentials)}**."
    )

# Group fields by category for clean UX
categories = {
    "financial": "💰 Financial & Transaction Measures",
    "transaction": "🧾 Order & Channel Attributes",
    "product": "📦 Product & Merchandise Hierarchy",
    "geography": "🗺️ Geography & Territory",
    "customer": "👥 Customer & Account Identifiers",
    "logistics": "🚚 Shipping & Logistics",
}

st.markdown("#### Review & Adjust Field Mappings")

# Build mapping form
with st.form("column_mapping_form"):
    for cat_key, cat_title in categories.items():
        st.markdown(f"##### {cat_title}")
        cat_fields = [f for f in STANDARD_BUSINESS_FIELDS.values() if f.category == cat_key]

        cols = st.columns(2)
        for idx, b_field in enumerate(cat_fields):
            current_mapped = mapper.current_mappings.get(b_field.key)
            default_index = 0
            if current_mapped and current_mapped in raw_cols:
                default_index = raw_cols.index(current_mapped)

            # Determine match confidence label
            conf = mapper.auto_result.confidence_scores.get(b_field.key, 0.0)
            tag = ""
            if b_field.key in mapper.auto_result.ambiguous_fields:
                tag = " ⚠️ [Ambiguous Candidate]"
            elif conf >= 0.9:
                tag = f" ✅ [Auto-matched {int(conf*100)}%]"
            elif conf > 0:
                tag = f" ℹ️ [Suggested {int(conf*100)}%]"

            star = " *" if b_field.is_essential else ""
            field_label = f"{b_field.display_name}{star}{tag}"

            target_col = cols[idx % 2]
            with target_col:
                selected_val = st.selectbox(
                    label=field_label,
                    options=raw_cols,
                    index=default_index,
                    key=f"map_select_{b_field.key}",
                    help=f"{b_field.description} (Internal key: {b_field.key})",
                )
                mapper.set_mapping(
                    b_field.key,
                    None if selected_val == "(Not Available / Unmapped)" else selected_val,
                )

        st.markdown("---")

    confirm_btn = st.form_submit_button(
        "💾 Confirm and Apply Column Mappings",
        type="primary",
        use_container_width=True,
    )

    if confirm_btn:
        st.session_state["column_mapper"] = mapper
        # Generate standardized DataFrame
        std_df = create_standard_dataframe(active_ds.raw_df, mapper.current_mappings)
        st.session_state["standard_df"] = std_df
        st.session_state["mapping_confirmed"] = True
        st.success("✅ Mappings confirmed! Standardized sales schema generated successfully.")
        st.rerun()

# Preview standardized schema if confirmed
if st.session_state.get("mapping_confirmed", False) and "standard_df" in st.session_state:
    st.markdown("#### Standardized Schema Preview")
    st.dataframe(
        st.session_state["standard_df"].head(5),
        use_container_width=True,
    )

# Bottom Navigation
can_advance = has_active_dataset() and is_essential_ok and st.session_state.get("mapping_confirmed", False)
block_reason = None
if not has_active_dataset():
    block_reason = "No active dataset loaded."
elif not is_essential_ok:
    block_reason = f"Essential fields unmapped: {', '.join(missing_essentials)}."
elif not st.session_state.get("mapping_confirmed", False):
    block_reason = "Please click 'Confirm and Apply Column Mappings' above before continuing."

render_step_navigation(
    current_step=4,
    prev_page="pages/3_Data_Inspection.py",
    next_page="pages/5_Analysis_Workspace.py",
    next_label="Advance to Analysis Workspace ➡️",
    can_advance=can_advance,
    blocking_message=block_reason,
)

render_app_footer()
