"""Tests for dataset ingestion, format validation, and encoding fallbacks."""

import io

import pytest

from src.data.loader import load_dataset
from src.utils.errors import (
    EmptyDataError,
    FileFormatError,
    FileSizeError,
)


def test_load_valid_csv(synthetic_sales_df, tmp_path):
    """Test loading a standard valid CSV file from disk."""
    csv_file = tmp_path / "valid_sales.csv"
    synthetic_sales_df.to_csv(csv_file, index=False)

    loaded = load_dataset(str(csv_file))
    assert loaded.file_format == "csv"
    assert loaded.total_rows == 5
    assert loaded.total_cols == 10
    assert loaded.file_name == "valid_sales.csv"
    assert "Sales" in loaded.raw_df.columns


def test_load_from_bytes_buffer(messy_sales_csv_bytes):
    """Test loading from an in-memory BytesIO buffer."""
    buf = io.BytesIO(messy_sales_csv_bytes)
    loaded = load_dataset(buf, file_name="messy.csv")

    assert loaded.total_rows == 3
    assert loaded.total_cols == 6
    assert "Sales Amount" in loaded.raw_df.columns


def test_load_unsupported_format(tmp_path):
    """Test that unsupported extensions trigger FileFormatError."""
    dummy_file = tmp_path / "document.pdf"
    dummy_file.write_text("dummy binary content")

    with pytest.raises(FileFormatError) as exc_info:
        load_dataset(str(dummy_file))
    assert "Unsupported file format" in str(exc_info.value)


def test_load_empty_file(tmp_path):
    """Test that an empty 0-byte file triggers EmptyDataError."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(EmptyDataError) as exc_info:
        load_dataset(str(empty_file))
    assert "completely empty" in str(exc_info.value)


def test_load_exceeds_max_size():
    """Test that files exceeding size limits trigger FileSizeError."""
    dummy_bytes = b"header1,header2\n1,2"
    buf = io.BytesIO(dummy_bytes)

    # Set artificial max size of 10 bytes
    with pytest.raises(FileSizeError):
        load_dataset(buf, file_name="big.csv", max_size_bytes=10)


def test_load_latin1_encoding(tmp_path):
    """Test reading CSV encoded with latin-1 characters (e.g. accented letters)."""
    csv_file = tmp_path / "latin_sales.csv"
    with open(csv_file, "w", encoding="latin-1") as f:
        f.write("Transaction,Café Revenue\n1,150.00\n2,280.50\n")

    loaded = load_dataset(str(csv_file))
    assert loaded.total_rows == 2
    assert loaded.encoding_used in ["latin-1", "iso-8859-1"]
