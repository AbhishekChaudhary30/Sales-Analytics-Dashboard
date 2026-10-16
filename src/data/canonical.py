"""Canonical Analytics Data Model and Schema Capability Verification.

Provides a unified interface between heterogeneous raw datasets, confirmed column mappings,
and derived business metrics without modifying original source data.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd

from src.config import STANDARD_BUSINESS_FIELDS


class FieldStatus(Enum):
    """Status of a canonical field in the analytical working dataset."""

    AVAILABLE = "available"
    DERIVED = "derived"
    UNAVAILABLE = "unavailable"


@dataclass
class CapabilityStatus:
    """Readiness assessment for an analytical module."""

    can_execute: bool
    required_fields: List[str]
    missing_fields: List[str] = field(default_factory=list)
    explanation: str = ""
    alternative_suggestion: str = ""


@dataclass
class CanonicalDataset:
    """Encapsulates the validated, normalized working copy of the dataset."""

    df: pd.DataFrame
    field_status: Dict[str, FieldStatus] = field(default_factory=dict)
    derived_fields: List[str] = field(default_factory=list)
    record_count: int = 0
    date_parsed_count: int = 0
    date_unparseable_count: int = 0
    currency_label: str = "USD"
    has_negative_sales: bool = False
    has_negative_profits: bool = False


def check_capability(
    dataset: Optional[CanonicalDataset], required_fields: List[str], module_name: str = "Analysis"
) -> CapabilityStatus:
    """Verify whether the canonical dataset possesses the required fields for a specific analysis."""
    if dataset is None or dataset.df is None or dataset.df.empty:
        return CapabilityStatus(
            can_execute=False,
            required_fields=required_fields,
            missing_fields=required_fields,
            explanation=f"{module_name} requires an active dataset with valid transaction records.",
            alternative_suggestion="Please upload or select a dataset first.",
        )

    missing: List[str] = []
    for req in required_fields:
        status = dataset.field_status.get(req, FieldStatus.UNAVAILABLE)
        if status == FieldStatus.UNAVAILABLE or req not in dataset.df.columns:
            # Check if column exists with non-null values
            missing.append(req)
        elif dataset.df[req].dropna().empty:
            missing.append(req)

    if missing:
        missing_names = [
            STANDARD_BUSINESS_FIELDS[f].display_name if f in STANDARD_BUSINESS_FIELDS else f
            for f in missing
        ]
        return CapabilityStatus(
            can_execute=False,
            required_fields=required_fields,
            missing_fields=missing,
            explanation=f"{module_name} requires: {', '.join(missing_names)}.",
            alternative_suggestion="Map the missing fields in Step 4: Column Mapping to enable this view.",
        )

    return CapabilityStatus(
        can_execute=True,
        required_fields=required_fields,
        missing_fields=[],
        explanation=f"All required fields for {module_name} are available.",
    )


def build_canonical_dataset(
    raw_df: pd.DataFrame,
    mappings: Dict[str, Optional[str]],
    currency_label: str = "USD",
    allow_derived_revenue: bool = True,
    allow_derived_profit: bool = True,
) -> CanonicalDataset:
    """Transform raw DataFrame into a CanonicalDataset using confirmed column mappings.

    Never invents data. Implements conservative derivation rules only when valid inputs exist.
    Preserves unmapped raw columns prefixed with 'unmapped_'.
    """
    clean_df = pd.DataFrame(index=raw_df.index)
    field_status: Dict[str, FieldStatus] = {k: FieldStatus.UNAVAILABLE for k in STANDARD_BUSINESS_FIELDS}
    derived_fields: List[str] = []

    # 1. Map explicitly confirmed fields
    for std_key, raw_col in mappings.items():
        if not raw_col or raw_col not in raw_df.columns:
            field_status[std_key] = FieldStatus.UNAVAILABLE
            continue

        raw_series = raw_df[raw_col]
        field_def = STANDARD_BUSINESS_FIELDS.get(std_key)
        data_type = field_def.data_type if field_def else "text"

        if data_type == "numeric":
            # Clean string symbols, commas, parentheses
            from src.utils.formatting import clean_numeric_series
            clean_df[std_key] = clean_numeric_series(raw_series)
            field_status[std_key] = FieldStatus.AVAILABLE
        elif data_type == "datetime":
            clean_df[std_key] = pd.to_datetime(raw_series, errors="coerce", format="mixed")
            field_status[std_key] = FieldStatus.AVAILABLE
        elif data_type == "id":
            clean_df[std_key] = raw_series.astype(str).str.strip()
            field_status[std_key] = FieldStatus.AVAILABLE
        else:
            clean_df[std_key] = raw_series.astype(str).str.strip()
            field_status[std_key] = FieldStatus.AVAILABLE

    # 2. Conservative revenue derivation if sales is not mapped
    if field_status.get("sales") != FieldStatus.AVAILABLE and allow_derived_revenue:
        if (
            field_status.get("quantity") == FieldStatus.AVAILABLE
            and field_status.get("unit_price") == FieldStatus.AVAILABLE
        ):
            clean_df["sales"] = clean_df["quantity"] * clean_df["unit_price"]
            field_status["sales"] = FieldStatus.DERIVED
            derived_fields.append("sales")

    # 3. Conservative profit derivation if profit is not mapped
    if field_status.get("profit") != FieldStatus.AVAILABLE and allow_derived_profit:
        if (
            field_status.get("sales") in (FieldStatus.AVAILABLE, FieldStatus.DERIVED)
            and field_status.get("cost") == FieldStatus.AVAILABLE
        ):
            clean_df["profit"] = clean_df["sales"] - clean_df["cost"]
            field_status["profit"] = FieldStatus.DERIVED
            derived_fields.append("profit")

    # 4. Check for negative sales and profits
    has_neg_sales = False
    if "sales" in clean_df.columns:
        valid_sales = clean_df["sales"].dropna()
        has_neg_sales = bool((valid_sales < 0).any())

    has_neg_profit = False
    if "profit" in clean_df.columns:
        valid_profit = clean_df["profit"].dropna()
        has_neg_profit = bool((valid_profit < 0).any())

    # 5. Date parsing telemetry
    date_parsed = 0
    date_unparseable = 0
    if "order_date" in clean_df.columns:
        date_parsed = int(clean_df["order_date"].notna().sum())
        date_unparseable = int(clean_df["order_date"].isna().sum())

    # 6. Preserve unmapped raw columns with prefix
    mapped_raw_cols = {v for v in mappings.values() if v is not None}
    for col in raw_df.columns:
        col_str = str(col)
        if col_str not in mapped_raw_cols:
            clean_df[f"unmapped_{col_str}"] = raw_df[col]

    return CanonicalDataset(
        df=clean_df,
        field_status=field_status,
        derived_fields=derived_fields,
        record_count=len(clean_df),
        date_parsed_count=date_parsed,
        date_unparseable_count=date_unparseable,
        currency_label=currency_label,
        has_negative_sales=has_neg_sales,
        has_negative_profits=has_neg_profit,
    )
