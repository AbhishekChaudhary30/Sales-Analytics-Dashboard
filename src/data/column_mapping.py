"""Confidence-based column mapping system for standard sales schema alignment."""

from dataclasses import dataclass, field
from difflib import SequenceMatcher

import pandas as pd

from src.config import STANDARD_BUSINESS_FIELDS, BusinessField
from src.utils.formatting import clean_numeric_series, normalize_column_name


@dataclass
class MappingCandidate:
    """Potential column match for a standard business field."""

    raw_column: str
    confidence: float  # 0.0 to 1.0
    match_reason: str  # 'exact_alias', 'normalized_alias', 'token_match', 'fuzzy'


@dataclass
class MappingResult:
    """Consolidated outcome of automatic schema detection."""

    # standard_key -> raw_column_name (or None if unmapped)
    detected_mappings: dict[str, str | None] = field(default_factory=dict)

    # standard_key -> confidence score
    confidence_scores: dict[str, float] = field(default_factory=dict)

    # standard_key -> List[MappingCandidate]
    candidate_matches: dict[str, list[MappingCandidate]] = field(default_factory=dict)

    # Fields requiring manual user confirmation
    ambiguous_fields: list[str] = field(default_factory=list)

    # Unmapped standard fields
    unmapped_fields: list[str] = field(default_factory=list)

    # Raw columns that remained unassigned
    unassigned_columns: list[str] = field(default_factory=list)


def calculate_similarity(a: str, b: str) -> float:
    """Calculate SequenceMatcher string similarity ratio."""
    return SequenceMatcher(None, a, b).ratio()


def score_column_match(raw_col: str, b_field: BusinessField) -> tuple[float, str]:
    """Score how well a raw column matches a business field definition.

    Returns:
        (confidence_score, match_reason)
    """
    raw_norm = normalize_column_name(raw_col)
    clean_aliases = [normalize_column_name(a) for a in b_field.aliases]

    # Exact alias match
    if raw_col.strip().lower() in [a.lower() for a in b_field.aliases]:
        return 1.0, "exact_alias"

    # Normalized alias match
    if raw_norm in clean_aliases:
        return 0.95, "normalized_alias"

    # Exact standard key match
    if raw_norm == b_field.key:
        return 0.95, "normalized_key"

    # Token overlap check (e.g. 'order_date_utc' contains 'order_date')
    raw_tokens = set(raw_norm.split("_"))
    for alias in clean_aliases:
        alias_tokens = set(alias.split("_"))
        if alias_tokens.issubset(raw_tokens):
            return 0.85, "token_match"

    # Fuzzy similarity check against highest-ranking alias
    best_ratio = 0.0
    for alias in clean_aliases:
        ratio = calculate_similarity(raw_norm, alias)
        best_ratio = max(best_ratio, ratio)

    if best_ratio >= 0.85:
        return round(best_ratio * 0.85, 2), "fuzzy"

    return 0.0, "no_match"


def auto_detect_mappings(raw_columns: list[str]) -> MappingResult:
    """Automatically detect candidate column mappings using confidence-based matching.

    Ensures ambiguous or multiple conflicting matches are flagged for explicit confirmation.
    """
    result = MappingResult()
    assigned_raw_cols: dict[str, str] = {}  # raw_col -> assigned_standard_key

    # Phase 1: Score all (field, raw_col) pairs
    all_scores: dict[str, list[MappingCandidate]] = {k: [] for k in STANDARD_BUSINESS_FIELDS}

    for key, b_field in STANDARD_BUSINESS_FIELDS.items():
        candidates: list[MappingCandidate] = []
        for col in raw_columns:
            score, reason = score_column_match(col, b_field)
            if score >= 0.70:
                candidates.append(
                    MappingCandidate(
                        raw_column=col,
                        confidence=score,
                        match_reason=reason,
                    )
                )

        # Sort candidates descending by confidence
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        all_scores[key] = candidates
        result.candidate_matches[key] = candidates

    # Phase 2: Assign high-confidence unique mappings first (>= 0.85)
    for key, candidates in all_scores.items():
        if not candidates:
            result.detected_mappings[key] = None
            result.confidence_scores[key] = 0.0
            result.unmapped_fields.append(key)
            continue

        top_cand = candidates[0]

        # Check for ambiguity: multiple top candidates with very close score
        if len(candidates) > 1 and (top_cand.confidence - candidates[1].confidence < 0.1):
            result.detected_mappings[key] = None
            result.confidence_scores[key] = top_cand.confidence
            result.ambiguous_fields.append(key)
            continue

        # Check if this raw column was already assigned to another field
        if top_cand.raw_column in assigned_raw_cols:
            prev_key = assigned_raw_cols[top_cand.raw_column]
            prev_conf = result.confidence_scores.get(prev_key, 0.0)
            if top_cand.confidence > prev_conf:
                # Reassign to current field, mark previous field as ambiguous
                result.detected_mappings[prev_key] = None
                result.ambiguous_fields.append(prev_key)
                result.detected_mappings[key] = top_cand.raw_column
                result.confidence_scores[key] = top_cand.confidence
                assigned_raw_cols[top_cand.raw_column] = key
            else:
                result.detected_mappings[key] = None
                result.ambiguous_fields.append(key)
        else:
            result.detected_mappings[key] = top_cand.raw_column
            result.confidence_scores[key] = top_cand.confidence
            assigned_raw_cols[top_cand.raw_column] = key

    # Collect unassigned raw columns
    assigned_set = {v for v in result.detected_mappings.values() if v is not None}
    result.unassigned_columns = [c for c in raw_columns if c not in assigned_set]

    return result


class ColumnMapper:
    """Manages manual overrides, mapping validations, and standard DataFrame construction."""

    def __init__(self, raw_columns: list[str]):
        self.raw_columns = raw_columns
        self.auto_result = auto_detect_mappings(raw_columns)
        self.current_mappings: dict[str, str | None] = dict(
            self.auto_result.detected_mappings
        )

    def set_mapping(self, standard_key: str, raw_col: str | None) -> None:
        """Update mapping for a specific business field."""
        if standard_key not in STANDARD_BUSINESS_FIELDS:
            return

        if raw_col in ["", "None", "(Not Available / Unmapped)", None]:
            self.current_mappings[standard_key] = None
        else:
            # If this raw_col was already mapped to another key, clear that key to prevent duplicate mapping
            for k, v in list(self.current_mappings.items()):
                if v == raw_col and k != standard_key:
                    self.current_mappings[k] = None
            self.current_mappings[standard_key] = raw_col

    def get_mapped_count(self) -> int:
        """Return number of currently mapped business fields."""
        return sum(1 for v in self.current_mappings.values() if v is not None)

    def get_essential_status(self) -> tuple[bool, list[str]]:
        """Verify whether essential fields (e.g. Sales, Order Date) are mapped."""
        missing_essentials: list[str] = []
        for key, field_def in STANDARD_BUSINESS_FIELDS.items():
            if field_def.is_essential and not self.current_mappings.get(key):
                missing_essentials.append(field_def.display_name)

        is_ready = len(missing_essentials) == 0
        return is_ready, missing_essentials


def create_standard_dataframe(
    raw_df: pd.DataFrame, mappings: dict[str, str | None]
) -> pd.DataFrame:
    """Generate a clean, standardized DataFrame using validated column mappings.

    Preserves original columns as `raw_{col}` while exposing clean standard fields
    with proper typing (numeric cleaned, datetime parsed).
    """
    clean_df = pd.DataFrame(index=raw_df.index)

    # 1. First copy mapped standard columns with type conversion
    for std_key, raw_col in mappings.items():
        if not raw_col or raw_col not in raw_df.columns:
            continue

        raw_series = raw_df[raw_col]
        field_def = STANDARD_BUSINESS_FIELDS.get(std_key)
        data_type = field_def.data_type if field_def else "text"

        if data_type == "numeric":
            clean_df[std_key] = clean_numeric_series(raw_series)
        elif data_type == "datetime":
            clean_df[std_key] = pd.to_datetime(raw_series, errors="coerce")
        elif data_type == "id":
            clean_df[std_key] = raw_series.astype(str).str.strip()
        else:  # categorical or text
            clean_df[std_key] = raw_series.astype(str).str.strip()

    # 2. Keep unmapped raw columns with a prefix so user never loses access to original columns
    mapped_raw_cols = {v for v in mappings.values() if v is not None}
    for col in raw_df.columns:
        col_str = str(col)
        if col_str not in mapped_raw_cols:
            clean_df[f"unmapped_{col_str}"] = raw_df[col]

    return clean_df
