"""Robust data loader supporting CSV and Excel files with encoding detection."""

import io
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from src.config import AppConfig
from src.utils.errors import (
    DataIngestionError,
    EmptyDataError,
    FileFormatError,
    FileSizeError,
)


@dataclass
class LoadedDataset:
    """Encapsulates raw uploaded data and ingestion metadata."""

    raw_df: pd.DataFrame
    file_name: str
    file_size_bytes: int
    file_format: str
    encoding_used: str | None
    load_timestamp: str
    total_rows: int
    total_cols: int


def get_file_details(
    file_input: Any, explicit_name: str | None = None
) -> tuple[str, int]:
    """Extract filename and size in bytes from various input sources."""
    # Streamlit UploadedFile
    if hasattr(file_input, "name") and hasattr(file_input, "size"):
        return file_input.name, file_input.size

    # File path on disk
    if isinstance(file_input, str):
        if not os.path.exists(file_input):
            raise DataIngestionError(
                f"File not found on disk: '{file_input}'",
                resolution_hint="Please verify the file path exists and is accessible.",
            )
        name = explicit_name or os.path.basename(file_input)
        size = os.path.getsize(file_input)
        return name, size

    # BytesIO / StringIO buffer
    if hasattr(file_input, "getbuffer"):
        size = file_input.getbuffer().nbytes
        name = explicit_name or "uploaded_file.csv"
        return name, size

    if hasattr(file_input, "getvalue"):
        val = file_input.getvalue()
        size = len(val) if isinstance(val, (bytes, str)) else 0
        name = explicit_name or "uploaded_file.csv"
        return name, size

    name = explicit_name or "unknown_file"
    return name, 0


def load_dataset(
    file_input: Any,
    file_name: str | None = None,
    max_size_bytes: int = AppConfig.MAX_FILE_SIZE_BYTES,
) -> LoadedDataset:
    """Load and ingest a dataset file (CSV or Excel) into memory safely.

    Args:
        file_input: File path, BytesIO, or Streamlit UploadedFile.
        file_name: Optional explicit file name override.
        max_size_bytes: Maximum allowed file size in bytes.

    Returns:
        LoadedDataset containing original DataFrame and ingestion telemetry.

    Raises:
        FileFormatError: If file extension is unsupported.
        FileSizeError: If file exceeds maximum allowed size.
        EmptyDataError: If file is 0 bytes or parses to an empty DataFrame.
        DataIngestionError: If file parsing fails across all candidate encodings.
    """
    detected_name, file_size = get_file_details(file_input, file_name)
    _, ext = os.path.splitext(detected_name.lower())

    if ext not in AppConfig.SUPPORTED_EXTENSIONS:
        raise FileFormatError(
            f"Unsupported file format '{ext}'. Expected one of: {', '.join(AppConfig.SUPPORTED_EXTENSIONS)}",
            resolution_hint="Please save your data as a CSV (.csv) or Excel (.xlsx) file and re-upload.",
        )

    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        max_mb = max_size_bytes / (1024 * 1024)
        raise FileSizeError(
            f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_mb:.0f} MB.",
            resolution_hint="Please filter or compress your dataset before uploading.",
        )

    # Read binary bytes into memory for consistent parsing & retry
    raw_bytes: bytes
    if isinstance(file_input, str):
        with open(file_input, "rb") as f:
            raw_bytes = f.read()
    elif hasattr(file_input, "seek") and hasattr(file_input, "read"):
        file_input.seek(0)
        raw_bytes = file_input.read()
        if isinstance(raw_bytes, str):
            raw_bytes = raw_bytes.encode("utf-8")
    elif isinstance(file_input, bytes):
        raw_bytes = file_input
    else:
        raise DataIngestionError(
            "Unrecognized file input format.",
            resolution_hint="Please provide a valid file buffer or file path.",
        )

    if not raw_bytes or len(raw_bytes.strip()) == 0:
        raise EmptyDataError(
            f"The uploaded file '{detected_name}' is completely empty (0 bytes).",
            resolution_hint="Please select a file that contains valid transaction rows.",
        )

    df: pd.DataFrame | None = None
    encoding_used: str | None = None

    if ext == ".csv":
        candidate_encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
        last_error = ""

        for enc in candidate_encodings:
            try:
                # First try standard comma/semicolon autodetect
                bio = io.BytesIO(raw_bytes)
                df = pd.read_csv(
                    bio,
                    encoding=enc,
                    sep=None,
                    engine="python",
                    on_bad_lines="skip",
                )
                encoding_used = enc
                break
            except Exception as e:
                last_error = str(e)
                # Try fallback with explicit comma
                try:
                    bio = io.BytesIO(raw_bytes)
                    df = pd.read_csv(
                        bio,
                        encoding=enc,
                        sep=",",
                        on_bad_lines="skip",
                    )
                    encoding_used = enc
                    break
                except Exception:
                    continue

        if df is None:
            raise DataIngestionError(
                f"Failed to parse CSV file '{detected_name}'. Details: {last_error}",
                resolution_hint=(
                    "Check if the CSV has a consistent delimiter (e.g. comma or semicolon) "
                    "and valid character encoding."
                ),
            )

    elif ext in [".xlsx", ".xls"]:
        try:
            bio = io.BytesIO(raw_bytes)
            engine = "openpyxl" if ext == ".xlsx" else None
            df = pd.read_excel(bio, engine=engine)
            encoding_used = "binary"
        except Exception as e:
            raise DataIngestionError(
                f"Failed to read Excel file '{detected_name}': {e!s}",
                resolution_hint="Ensure the Excel spreadsheet is not password-protected or corrupted.",
            )

    if df is None or df.empty:
        raise EmptyDataError(
            f"The dataset '{detected_name}' parsed with 0 data rows.",
            resolution_hint="Verify that the file contains actual table data and not just blank lines.",
        )

    return LoadedDataset(
        raw_df=df.copy(deep=True),
        file_name=detected_name,
        file_size_bytes=len(raw_bytes),
        file_format=ext.lstrip("."),
        encoding_used=encoding_used,
        load_timestamp=datetime.now(timezone.utc).isoformat(),
        total_rows=len(df),
        total_cols=len(df.columns),
    )
