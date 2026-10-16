# Data Directory

This directory contains static sample datasets used for demonstration and testing.

## Privacy & Handling
- **No Permanent User Storage**: Files uploaded by users through the Streamlit web interface are processed **in-memory** within the active Python session and are never saved permanently to disk.
- **Git Exclusions**: The `.gitignore` file explicitly excludes personal datasets and upload folders (`data/uploads/`, `*.tmp`).
- **Test Fixtures**: Automated tests use synthetic data fixtures located under `tests/` and do not require internet access.
