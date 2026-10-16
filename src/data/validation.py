"""Structural validation of imported datasets.

Checks row and column dimensions, duplicate headers, blank columns,
unnamed indexes, and delimitation consistency without mutating the raw data.
"""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ValidationResult:
    """Encapsulates the findings of structural dataset validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sanitized_columns: list[str] = field(default_factory=list)
    duplicate_columns: list[str] = field(default_factory=list)
    empty_columns: list[str] = field(default_factory=list)
    unnamed_columns: list[str] = field(default_factory=list)
    blank_rows_count: int = 0


def sanitize_column_names(columns: list[str]) -> tuple[list[str], list[str]]:
    """Deduplicate and clean column headers, returning (clean_names, duplicate_names)."""
    seen: dict = {}
    sanitized: list[str] = []
    duplicates: list[str] = []

    for idx, col in enumerate(columns):
        name = str(col).strip() if col is not None else f"Column_{idx + 1}"
        if not name:
            name = f"Column_{idx + 1}"

        lower_name = name.lower()
        if lower_name in seen:
            seen[lower_name] += 1
            dedup_name = f"{name}_{seen[lower_name]}"
            duplicates.append(name)
            sanitized.append(dedup_name)
        else:
            seen[lower_name] = 0
            sanitized.append(name)

    return sanitized, list(set(duplicates))


def validate_dataset(df: pd.DataFrame) -> ValidationResult:
    """Perform non-destructive structural checks on a loaded dataset.

    Args:
        df: Raw pandas DataFrame to validate.

    Returns:
        ValidationResult containing pass/fail state, diagnostic errors, and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if df is None or df.empty:
        return ValidationResult(
            is_valid=False,
            errors=["Dataset is completely empty and contains no rows or columns."],
        )

    # 1. Row count check
    if len(df) == 0:
        errors.append("Dataset has no transaction rows.")

    # 2. Column count check
    raw_cols = [str(c) for c in df.columns]
    if len(raw_cols) < 2:
        warnings.append(
            f"Dataset has only {len(raw_cols)} column. If this is a CSV, verify that the delimiter "
            "(comma, semicolon, tab) was recognized properly."
        )

    # 3. Deduplicate / sanitize headers
    sanitized_cols, dup_cols = sanitize_column_names(raw_cols)
    if dup_cols:
        warnings.append(
            f"Detected {len(dup_cols)} duplicate column name(s): {', '.join(dup_cols[:5])}. "
            "Unique numeric suffixes will be assigned for mapping safety."
        )

    # 4. Unnamed columns detection (e.g. index exported accidentally)
    unnamed_cols = [c for c in raw_cols if c.startswith("Unnamed:") or c.strip() == ""]
    if unnamed_cols:
        warnings.append(
            f"Detected {len(unnamed_cols)} unnamed column(s). These frequently represent row numbers "
            "or export artifacts."
        )

    # 5. Empty columns detection (all NaN)
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        warnings.append(
            f"Found {len(empty_cols)} column(s) with 100% missing values: {', '.join(str(c) for c in empty_cols[:4])}."
        )

    # 6. Completely blank rows count
    blank_rows = int(df.isna().all(axis=1).sum())
    if blank_rows > 0:
        warnings.append(
            f"Found {blank_rows:,} completely empty row(s) in the dataset."
        )

    is_valid = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_columns=sanitized_cols,
        duplicate_columns=dup_cols,
        empty_columns=[str(c) for c in empty_cols],
        unnamed_columns=unnamed_cols,
        blank_rows_count=blank_rows,
    )
