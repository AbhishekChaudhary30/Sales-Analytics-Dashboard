# Multipage Navigation Pages

This directory contains the individual step pages executed via Streamlit's modern `st.navigation` and `st.Page` API.

## Workflow Structure
1. `1_Overview.py` (Step 1): Welcome, application capabilities, sample dataset quick-loader, and supported formats.
2. `2_Upload_Data.py` (Step 2): Drag-and-drop file uploader with extension and size validation, encoding fallback, and instant validation status.
3. `3_Data_Inspection.py` (Step 3): In-depth data profiling, summary metrics, raw data preview with pagination/filters, and data quality warnings.
4. `4_Column_Mapping.py` (Step 4): Confidence-based auto-detection of standard business fields, candidate review, manual overrides, and essential field validation.
5. `5_Analysis_Workspace.py` (Step 5): Initial KPI view and visualization readiness assessment (expanded in Phase 2).
6. `6_Reports_and_Export.py` (Step 6): Data export preview and reporting workflow placeholder (expanded in Phase 2).
