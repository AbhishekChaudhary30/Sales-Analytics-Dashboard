"""Automated regression tests verifying zero raw HTML/code leakage across UI components and pages."""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
from streamlit.testing.v1 import AppTest


def test_render_html_no_code_block_generation():
    """Verify that render_html does not emit indented code blocks."""
    test_script = """
import streamlit as st
from src.ui.layout import render_html

render_html('''
    <div class="custom-card">
        <span class="badge">Active</span>
        <p>Details here</p>
    </div>
''')
"""
    at = AppTest.from_string(test_script)
    at.run()
    assert not at.exception
    # Assert no code elements exist
    assert len(at.code) == 0


def test_render_app_header_no_dataset():
    """Verify header renders without leaking HTML into code or raw text."""
    test_script = """
import streamlit as st
from src.ui.layout import render_app_header
render_app_header(dataset_name=None, row_count=0)
"""
    at = AppTest.from_string(test_script)
    at.run()
    assert not at.exception
    assert len(at.code) == 0


def test_render_app_header_with_dataset():
    """Verify header with active dataset does not leak HTML tags."""
    test_script = """
import streamlit as st
from src.ui.layout import render_app_header
render_app_header(dataset_name="Superstore_Sales.csv", row_count=9994)
"""
    at = AppTest.from_string(test_script)
    at.run()
    assert not at.exception
    assert len(at.code) == 0


def test_render_step_indicator():
    """Verify step indicator bar does not break into code blocks."""
    test_script = """
import streamlit as st
from src.ui.components import render_step_indicator
for step in range(1, 7):
    render_step_indicator(step)
"""
    at = AppTest.from_string(test_script)
    at.run()
    assert not at.exception
    assert len(at.code) == 0


def test_render_all_reusable_components():
    """Verify metric cards, section headings, empty states, and warnings do not leak code."""
    test_script = """
import streamlit as st
from src.ui.components import (
    render_metric_card,
    render_section_heading,
    render_empty_state,
    render_quality_warnings_box,
)

render_section_heading("Test Section", "Subtitle", icon="[*]")
render_metric_card("Revenue", "$120,000", sublabel="Gross volume", icon="[$]")
render_empty_state("No Records", "Please load a file", icon="[D]")
render_quality_warnings_box(["Warning 1: Missing sales", "Warning 2: Duplicates"])
render_quality_warnings_box([])
"""
    at = AppTest.from_string(test_script)
    at.run()
    assert not at.exception
    assert len(at.code) == 0


def test_overview_page_apptest_clean_rendering():
    """Verify Page 1 Overview runs cleanly without generating raw HTML code elements."""
    at = AppTest.from_file("pages/1_Overview.py", default_timeout=30)
    at.run()
    assert not at.exception
    # Verify no code elements contain leaked HTML tags
    for code_elem in at.code:
        assert "<div" not in code_elem.value
        assert "<span" not in code_elem.value
