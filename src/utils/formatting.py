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


CURRENCY_MAP = {
    "USD": "$",
    "INR": "₹",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CAD": "C$",
    "AUD": "A$",
}


def format_indian_currency(val_float: float, symbol: str = "₹") -> str:
    """Format numeric values using the Indian numbering system (Lakhs and Crores)."""
    is_neg = val_float < 0
    abs_val = abs(val_float)

    if abs_val >= 10_000_000:
        return f"{'-' if is_neg else ''}{symbol}{abs_val / 10_000_000:.2f} Cr"
    if abs_val >= 100_000:
        return f"{'-' if is_neg else ''}{symbol}{abs_val / 100_000:.2f} L"

    # Indian comma grouping: 12,34,567.89
    s = f"{abs_val:.2f}"
    parts = s.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) > 3:
        last3 = integer_part[-3:]
        rest = integer_part[:-3]
        # Group remaining digits in pairs from right to left
        grouped_pairs = []
        while len(rest) > 2:
            grouped_pairs.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            grouped_pairs.insert(0, rest)
        formatted_int = ",".join(grouped_pairs) + "," + last3
    else:
        formatted_int = integer_part

    return f"{'-' if is_neg else ''}{symbol}{formatted_int}.{decimal_part}"


def format_currency(
    val: float | None,
    currency_or_symbol: str = "USD",
    use_indian_format: bool = False,
) -> str:
    """Format numeric values as clean currency strings supporting international and Indian formats."""
    if val is None or pd.isna(val):
        return "—"
    try:
        val_float = float(val)
        symbol = CURRENCY_MAP.get(currency_or_symbol.upper(), currency_or_symbol)

        if use_indian_format or currency_or_symbol.upper() == "INR":
            return format_indian_currency(val_float, symbol)

        is_neg = val_float < 0
        abs_val = abs(val_float)
        prefix = f"-{symbol}" if is_neg else symbol

        if abs_val >= 1_000_000_000:
            return f"{prefix}{abs_val / 1_000_000_000:,.2f}B"
        if abs_val >= 1_000_000:
            return f"{prefix}{abs_val / 1_000_000:,.2f}M"
        if abs_val >= 1_000:
            return f"{prefix}{abs_val:,.2f}"
        return f"{prefix}{abs_val:.2f}"
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
