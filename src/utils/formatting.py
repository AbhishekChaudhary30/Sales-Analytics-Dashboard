"""Text formatting, number formatting, and column name normalization utilities."""

import re
from typing import Any

import pandas as pd


def normalize_column_name(col: Any) -> str:
    """Normalize a raw column header string for robust matching.

    Examples:
        'Order Date' -> 'order_date'
        'Sales Amount ($)' -> 'sales_amount'
        'Sub-Category' -> 'sub_category'
        '  Units Sold  ' -> 'units_sold'
    """
    if col is None:
        return ""
    text = str(col).strip().lower()
    # Replace punctuation separators (hyphens, slashes, dots, whitespace) with underscores
    text = re.sub(r"[\s\-\/\.]+", "_", text)
    # Remove any remaining non-alphanumeric characters except underscore
    text = re.sub(r"[^\w]", "", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def clean_numeric_series(series: pd.Series) -> pd.Series:
    """Convert a messy string series containing currency/commas to numeric float.

    Handles:
        '$1,240.50' -> 1240.50
        ' (450.00) ' -> -450.00
        '12.5%' -> 0.125 or 12.5
        '€ 99.95' -> 99.95
    """
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    # Work with string representation
    cleaned = series.astype(str).str.strip()

    # Handle negative values written as parentheses: (123.45) -> -123.45
    cleaned = cleaned.str.replace(r"^\((.*)\)$", r"-\1", regex=True)

    # Remove currency symbols, commas, and trailing percent signs if present
    cleaned = cleaned.str.replace(r"[\$,€,£,¥,\s]", "", regex=True)

    # Convert to numeric float
    numeric = pd.to_numeric(cleaned, errors="coerce")
    return numeric


def format_currency(val: float | None, symbol: str = "$") -> str:
    """Format numeric values as clean currency strings."""
    if val is None or pd.isna(val):
        return "—"
    try:
        val_float = float(val)
        if abs(val_float) >= 1_000_000:
            return f"{symbol}{val_float / 1_000_000:,.2f}M"
        if abs(val_float) >= 1_000:
            return f"{symbol}{val_float:,.2f}"
        return f"{symbol}{val_float:.2f}"
    except (ValueError, TypeError):
        return "—"


def format_number(val: float | None, precision: int = 0) -> str:
    """Format large numbers with readable commas or K/M abbreviations."""
    if val is None or pd.isna(val):
        return "—"
    try:
        val_float = float(val)
        if abs(val_float) >= 1_000_000:
            return f"{val_float / 1_000_000:,.2f}M"
        if abs(val_float) >= 10_000:
            return f"{val_float:,.{precision}f}"
        if precision > 0:
            return f"{val_float:.{precision}f}"
        return f"{int(round(val_float)):,}"
    except (ValueError, TypeError):
        return "—"


def format_percentage(val: float | None, precision: int = 1) -> str:
    """Format decimal or percentage values as clean strings."""
    if val is None or pd.isna(val):
        return "—"
    try:
        val_float = float(val)
        # If value is between 0 and 1, caller might mean a fraction, but let's format given value
        return f"{val_float:+.{precision}f}%" if val_float != 0 else f"{val_float:.{precision}f}%"
    except (ValueError, TypeError):
        return "—"


def format_filesize(size_bytes: int) -> str:
    """Format bytes into readable KB/MB string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"
