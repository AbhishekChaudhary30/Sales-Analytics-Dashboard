"""Custom exceptions and safe error display utilities.

Ensures users receive understandable, actionable guidance instead of raw
stack traces when file ingestion, validation, or mapping issues occur.
"""



class DashboardError(Exception):
    """Base exception for all domain-specific dashboard errors."""

    def __init__(self, message: str, resolution_hint: str | None = None):
        super().__init__(message)
        self.message = message
        self.resolution_hint = resolution_hint or "Please review the uploaded file and try again."

    def to_user_dict(self) -> dict[str, str]:
        """Convert exception to user-friendly presentation dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "resolution_hint": self.resolution_hint,
        }


class DataIngestionError(DashboardError):
    """Raised when reading or parsing a file fails."""


class FileFormatError(DataIngestionError):
    """Raised when an unsupported file extension is provided."""


class FileSizeError(DataIngestionError):
    """Raised when file exceeds the maximum allowed upload size."""


class EmptyDataError(DataIngestionError):
    """Raised when an uploaded file contains 0 rows or is completely blank."""


class DataValidationError(DashboardError):
    """Raised when dataset structure violates core validation rules."""


class ColumnMappingError(DashboardError):
    """Raised when column mapping is contradictory, incomplete, or invalid."""


def format_error_for_ui(exc: Exception) -> dict[str, str]:
    """Format any caught exception into a safe, elegant UI feedback dictionary."""
    if isinstance(exc, DashboardError):
        return exc.to_user_dict()

    # Generic unhandled exception: conceal raw traces, give safe explanation
    return {
        "error_type": "UnexpectedProcessingError",
        "message": f"An unexpected issue occurred while processing your data: {exc!s}",
        "resolution_hint": (
            "Please check that your file is not password-protected, corrupted, "
            "or open in another application, then try uploading again."
        ),
    }
