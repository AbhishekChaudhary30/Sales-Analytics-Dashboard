"""Session state management and guided step-by-step navigation controls."""

from typing import Any

import streamlit as st


def init_session_state() -> None:
    """Initialize all persistent session state variables safely."""
    defaults: dict[str, Any] = {
        "raw_dataset": None,
        "dataset_profile": None,
        "column_mapper": None,
        "standard_df": None,
        "current_step": 1,
        "sample_loaded": False,
        "mapping_confirmed": False,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_current_dataset() -> Any | None:
    """Retrieve currently active LoadedDataset if present in session state."""
    return st.session_state.get("raw_dataset", None)


def has_active_dataset() -> bool:
    """Check whether a valid dataset has been ingested into memory."""
    dataset = get_current_dataset()
    return dataset is not None and dataset.raw_df is not None and not dataset.raw_df.empty


def render_step_navigation(
    current_step: int,
    prev_page: str | None = None,
    next_page: str | None = None,
    next_label: str = "Continue to Next Step ➡️",
    can_advance: bool = True,
    blocking_message: str | None = None,
) -> None:
    """Render bottom Previous / Next navigation bar with validation guarding."""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if prev_page:
            if st.button("⬅️ Previous Step", key=f"prev_btn_step_{current_step}", use_container_width=True):
                st.session_state["current_step"] = max(1, current_step - 1)
                st.switch_page(prev_page)

    with col2:
        if not can_advance and blocking_message:
            st.warning(f"⚠️ {blocking_message}")

    with col3:
        if next_page:
            btn_clicked = st.button(
                next_label,
                key=f"next_btn_step_{current_step}",
                type="primary",
                disabled=not can_advance,
                use_container_width=True,
            )
            if btn_clicked:
                if can_advance:
                    st.session_state["current_step"] = current_step + 1
                    st.switch_page(next_page)
                else:
                    st.error(blocking_message or "Please resolve required inputs before proceeding.")
