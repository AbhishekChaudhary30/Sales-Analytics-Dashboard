"""Comprehensive dataset profiling and exploratory data quality auditing."""

from dataclasses import dataclass, field

import pandas as pd

from src.utils.formatting import (
    clean_numeric_series,
    format_filesize,
    normalize_column_name,
)


@dataclass
class ColumnProfile:
    """Statistical and semantic profile for a single column."""

    column_name: str
    raw_dtype: str
    semantic_type: str  # 'numeric', 'datetime', 'categorical', 'id', 'text'
    non_null_count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    is_unique: bool
    sample_values: list[str] = field(default_factory=list)

    # Numeric metrics (if applicable)
    num_min: float | None = None
    num_max: float | None = None
    num_mean: float | None = None
    num_median: float | None = None
    num_std: float | None = None
    num_q25: float | None = None
    num_q75: float | None = None

    # Datetime metrics (if applicable)
    date_min: str | None = None
    date_max: str | None = None
    date_range_days: int | None = None

    # Categorical metrics (if applicable)
    top_categories: dict[str, int] = field(default_factory=dict)


@dataclass
class DatasetProfile:
    """Complete structural, statistical, and quality profile of a dataset."""

    total_rows: int
    total_cols: int
    memory_bytes: int
    memory_formatted: str
    duplicate_rows_count: int
    duplicate_rows_percentage: float
    columns_profile: dict[str, ColumnProfile] = field(default_factory=dict)

    # Classification buckets
    candidate_id_cols: list[str] = field(default_factory=list)
    candidate_numeric_cols: list[str] = field(default_factory=list)
    candidate_datetime_cols: list[str] = field(default_factory=list)
    candidate_categorical_cols: list[str] = field(default_factory=list)
    candidate_sales_cols: list[str] = field(default_factory=list)

    # Actionable quality warnings
    quality_warnings: list[str] = field(default_factory=list)


def infer_column_semantic_type(
    series: pd.Series, col_name: str
) -> tuple[str, pd.Series | None]:
    """Infer high-level semantic type: 'datetime', 'numeric', 'id', 'categorical', or 'text'.

    Returns (semantic_type, converted_series_or_None).
    """
    norm = normalize_column_name(col_name)

    # Check 1: Already datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime", series

    # Check 2: Column name or string data looks like a date
    date_clues = ["date", "time", "timestamp", "year", "month", "day", "period"]
    has_date_name = any(k in norm for k in date_clues)
    non_null = series.dropna()

    if len(non_null) > 0 and (has_date_name or series.dtype == "object"):
        # Sample up to 50 rows to test datetime conversion without heavy overhead
        sample = non_null.head(50).astype(str)
        # Avoid treating pure short numbers like '2024' or '1' as timestamps accidentally unless date clue
        pure_numeric = sample.str.replace(".", "", regex=False).str.isdigit()
        if not (pure_numeric.all() and not has_date_name):
            try:
                parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
                valid_ratio = parsed.notna().sum() / len(sample)
                if valid_ratio >= 0.7:
                    full_parsed = pd.to_datetime(series, errors="coerce", format="mixed")
                    return "datetime", full_parsed
            except Exception:
                pass

    # Check 3: Numeric (already numeric or formatted currency/numbers)
    if pd.api.types.is_numeric_dtype(series):
        # Could be an ID column if all integers and ends with 'id'
        if norm.endswith("id") or norm.endswith("_id") or norm == "id":
            return "id", None
        return "numeric", series

    if series.dtype == "object" and len(non_null) > 0:
        cleaned_num = clean_numeric_series(non_null.head(50))
        if cleaned_num.notna().sum() / len(cleaned_num) >= 0.85:
            full_cleaned = clean_numeric_series(series)
            if norm.endswith("id") or norm.endswith("_id"):
                return "id", None
            return "numeric", full_cleaned

    # Check 4: ID column by name
    id_clues = ["_id", "id", "code", "sku", "number", "no", "key", "uuid"]
    if any(norm.endswith(k) or norm.startswith(k) for k in id_clues):
        return "id", None

    # Check 5: Categorical vs Free Text
    unique_count = series.nunique(dropna=True)
    total_non_null = len(non_null)

    if total_non_null > 0:
        cardinality_ratio = unique_count / total_non_null
        if unique_count <= 60 or cardinality_ratio < 0.2:
            return "categorical", None

    return "text", None


def profile_dataset(df: pd.DataFrame) -> DatasetProfile:
    """Generate an in-depth data profile with quality checks and column telemetry.

    Args:
        df: Input DataFrame to profile.

    Returns:
        DatasetProfile with column-level metrics and quality warnings.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    mem_bytes = int(df.memory_usage(deep=True).sum())
    mem_formatted = format_filesize(mem_bytes)

    # Duplicate rows check
    dup_rows = int(df.duplicated().sum()) if total_rows > 0 else 0
    dup_pct = (dup_rows / total_rows * 100.0) if total_rows > 0 else 0.0

    cols_profile: dict[str, ColumnProfile] = {}
    id_cols: list[str] = []
    numeric_cols: list[str] = []
    datetime_cols: list[str] = []
    categorical_cols: list[str] = []
    sales_cols: list[str] = []
    warnings: list[str] = []

    sales_keywords = ["sales", "revenue", "amount", "total", "turnover", "price", "profit"]

    for col in df.columns:
        col_str = str(col)
        series = df[col]
        non_null_count = int(series.notna().sum())
        missing_count = total_rows - non_null_count
        missing_pct = (missing_count / total_rows * 100.0) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))
        is_unique = (unique_count == total_rows) and (total_rows > 0)

        # Non-null sample values for quick inspection
        sample_vals = [str(x) for x in series.dropna().unique()[:4]]

        sem_type, converted_series = infer_column_semantic_type(series, col_str)

        col_prof = ColumnProfile(
            column_name=col_str,
            raw_dtype=str(series.dtype),
            semantic_type=sem_type,
            non_null_count=non_null_count,
            missing_count=missing_count,
            missing_percentage=round(missing_pct, 2),
            unique_count=unique_count,
            is_unique=is_unique,
            sample_values=sample_vals,
        )

        norm_name = normalize_column_name(col_str)

        # Process Numeric telemetry
        if sem_type == "numeric":
            target_series = converted_series if converted_series is not None else series
            clean_num = pd.to_numeric(target_series, errors="coerce").dropna()
            if not clean_num.empty:
                col_prof.num_min = float(clean_num.min())
                col_prof.num_max = float(clean_num.max())
                col_prof.num_mean = round(float(clean_num.mean()), 2)
                col_prof.num_median = round(float(clean_num.median()), 2)
                col_prof.num_std = round(float(clean_num.std()), 2) if len(clean_num) > 1 else 0.0
                col_prof.num_q25 = round(float(clean_num.quantile(0.25)), 2)
                col_prof.num_q75 = round(float(clean_num.quantile(0.75)), 2)

            numeric_cols.append(col_str)
            if any(k in norm_name for k in sales_keywords):
                sales_cols.append(col_str)

        elif sem_type == "datetime":
            target_dates = converted_series if converted_series is not None else pd.to_datetime(series, errors="coerce")
            valid_dates = target_dates.dropna()
            if not valid_dates.empty:
                d_min = valid_dates.min()
                d_max = valid_dates.max()
                col_prof.date_min = d_min.strftime("%Y-%m-%d")
                col_prof.date_max = d_max.strftime("%Y-%m-%d")
                col_prof.date_range_days = (d_max - d_min).days

            datetime_cols.append(col_str)

        elif sem_type == "categorical":
            top_vc = series.value_counts(dropna=True).head(5).to_dict()
            col_prof.top_categories = {str(k): int(v) for k, v in top_vc.items()}
            categorical_cols.append(col_str)

        elif sem_type == "id":
            id_cols.append(col_str)

        # High missing value warning (> 30%)
        if missing_pct >= 30.0:
            warnings.append(
                f"Column '{col_str}' has {missing_pct:.1f}% missing values ({missing_count:,} rows)."
            )

        cols_profile[col_str] = col_prof

    # Overall dataset warnings
    if dup_pct >= 5.0:
        warnings.append(
            f"Dataset contains {dup_rows:,} duplicate rows ({dup_pct:.1f}% of total). "
            "Examine whether these are repeated line items or redundant exports."
        )

    if not datetime_cols:
        warnings.append(
            "No standard datetime column detected. Time-series and trend analyses may require manual mapping."
        )

    if not sales_cols and not numeric_cols:
        warnings.append(
            "No numeric sales or financial measure detected. Financial KPIs cannot be calculated without revenue data."
        )

    return DatasetProfile(
        total_rows=total_rows,
        total_cols=total_cols,
        memory_bytes=mem_bytes,
        memory_formatted=mem_formatted,
        duplicate_rows_count=dup_rows,
        duplicate_rows_percentage=round(dup_pct, 2),
        columns_profile=cols_profile,
        candidate_id_cols=id_cols,
        candidate_numeric_cols=numeric_cols,
        candidate_datetime_cols=datetime_cols,
        candidate_categorical_cols=categorical_cols,
        candidate_sales_cols=sales_cols,
        quality_warnings=warnings,
    )
