"""Data ingestion, validation, profiling, and mapping modules."""

from src.data.canonical import (
    CanonicalDataset,
    CapabilityStatus,
    FieldStatus,
    build_canonical_dataset,
    check_capability,
)
from src.data.column_mapping import (
    ColumnMapper,
    MappingCandidate,
    MappingResult,
    auto_detect_mappings,
    create_standard_dataframe,
)
from src.data.loader import LoadedDataset, load_dataset
from src.data.profiling import ColumnProfile, DatasetProfile, profile_dataset
from src.data.validation import ValidationResult, validate_dataset

__all__ = [
    "CanonicalDataset",
    "CapabilityStatus",
    "ColumnMapper",
    "ColumnProfile",
    "DatasetProfile",
    "FieldStatus",
    "LoadedDataset",
    "MappingCandidate",
    "MappingResult",
    "ValidationResult",
    "auto_detect_mappings",
    "build_canonical_dataset",
    "check_capability",
    "create_standard_dataframe",
    "load_dataset",
    "profile_dataset",
    "validate_dataset",
]
