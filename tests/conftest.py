"""Pytest fixtures providing synthetic, offline dataset variations for automated testing."""

import pandas as pd
import pytest


@pytest.fixture
def synthetic_sales_df() -> pd.DataFrame:
    """A clean, realistic synthetic sales dataframe."""
    return pd.DataFrame({
        "Order ID": ["ORD-101", "ORD-102", "ORD-103", "ORD-104", "ORD-105"],
        "Order Date": ["2024-01-15", "2024-01-16", "2024-02-10", "2024-02-12", "2024-03-01"],
        "Customer Name": ["Alice Smith", "Bob Jones", "Carol White", "Dan Brown", "Eve Davis"],
        "Category": ["Technology", "Furniture", "Technology", "Office Supplies", "Furniture"],
        "Sub-Category": ["Phones", "Chairs", "Accessories", "Paper", "Tables"],
        "Sales": [1200.50, 450.00, 89.90, 34.50, 680.00],
        "Quantity": [2, 1, 3, 5, 2],
        "Discount": [0.10, 0.0, 0.05, 0.0, 0.20],
        "Profit": [240.10, 80.00, 25.50, 12.00, -45.00],
        "Region": ["East", "West", "Central", "South", "East"],
    })


@pytest.fixture
def messy_sales_csv_bytes() -> bytes:
    """CSV bytes containing currency symbols, commas, and percentage strings."""
    csv_str = (
        "Invoice No,Invoice Date,Item Description,Customer,Sales Amount,Profit Margin\n"
        "INV-001,2023-05-10,Widget A,Acme Corp,$1,250.00,15.5%\n"
        "INV-002,2023-05-11,Widget B,Beta LLC,$450.50,22.0%\n"
        "INV-003,2023-05-12,Widget C,Gamma Inc,($120.00),-5.0%\n"
    )
    return csv_str.encode("utf-8")


@pytest.fixture
def duplicate_columns_df() -> pd.DataFrame:
    """Dataframe with duplicate and unnamed column names."""
    data = [[1, 2, 3], [4, 5, 6]]
    cols = ["Sales", "Sales", "Unnamed: 0"]
    return pd.DataFrame(data, columns=cols)


@pytest.fixture
def empty_csv_bytes() -> bytes:
    """Empty 0-byte stream."""
    return b""
