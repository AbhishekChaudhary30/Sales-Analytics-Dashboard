"""Tests for structural dataset validation and column header sanitization."""

import pandas as pd

from src.data.validation import sanitize_column_names, validate_dataset


def test_sanitize_column_names_deduplication():
    """Test deduplicating repeated column names safely."""
    cols = ["Sales", "Sales", "Customer", "sales", ""]
    sanitized, duplicates = sanitize_column_names(cols)

    assert "Sales" in sanitized
    assert "Sales_1" in sanitized
    assert "sales_2" in sanitized
    assert "Column_5" in sanitized
    assert len(duplicates) >= 1


def test_validate_empty_dataframe():
    """Test validating an empty dataframe."""
    df = pd.DataFrame()
    res = validate_dataset(df)
    assert not res.is_valid
    assert len(res.errors) > 0


def test_validate_single_column_warning():
    """Test that a single-column dataframe generates a delimitation warning."""
    df = pd.DataFrame({"col_only": [1, 2, 3]})
    res = validate_dataset(df)
    assert res.is_valid  # Structurally permissible but flagged
    assert any("delimiter" in w.lower() for w in res.warnings)


def test_validate_unnamed_and_empty_columns():
    """Test detecting unnamed headers and 100% missing columns."""
    df = pd.DataFrame({
        "Unnamed: 0": [0, 1, 2],
        "Sales": [100.0, 200.0, 300.0],
        "EmptyCol": [None, None, None],
    })
    res = validate_dataset(df)
    assert res.is_valid
    assert len(res.unnamed_columns) == 1
    assert "EmptyCol" in res.empty_columns
    assert any("unnamed" in w.lower() for w in res.warnings)
