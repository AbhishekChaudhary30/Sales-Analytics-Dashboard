# Architecture & Technical Design

This document details the modular software architecture, data ingestion lifecycle, session state architecture, and UI/UX conventions powering the **Sales Analytics Dashboard**.

---

## 1. High-Level Architecture Overview

The system strictly adheres to the **Separation of Concerns (SoC)** principle, isolating user interface widgets from business metrics, visualization rendering, and low-level data transformation:

```
┌────────────────────────────────────────────────────────┐
│                   STREAMLIT WEB UI                     │
│  (app.py, pages/1..6, src/ui/components, layout, filters│
└──────────────────────────┬─────────────────────────────┘
                           │ Dispatches user interactions
                           ▼
┌────────────────────────────────────────────────────────┐
│                 SESSION STATE ENGINE                   │
│   (raw_dataset, dataset_profile, canonical_dataset,    │
│    active_filters, selected_currency, active_tab)      │
└────────────┬─────────────────────────────┬─────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────┐
│   DATA PIPELINE LAYER   │   │     ANALYTICS ENGINE     │
│   - Ingestion (loader)  │   │   - Canonical Data Model │
│   - Validation (schema) │   │   - Executive Metrics    │
│   - Profiling (telemetry│   │   - Time-Series Engine   │
│   - Column Alignment    │   │   - Products & Pareto    │
│     (confidence scoring)│   │   - Geography/Territory  │
│   - Canonical Model     │   │   - Customer Intelligence│
│     (safe derivations)  │   │   - Profitability/Elastic│
└────────────┬────────────┘   │   - Statistical Hub      │
             │                │   - Dynamic Filter Engine│
             │                │   - Evidence-Based Signals│
             │                └────────────┬─────────────┘
             │                             │
             └──────────────┬──────────────┘
                            │ Filtered Canonical DataFrame
                            ▼
┌────────────────────────────────────────────────────────┐
│              VISUALIZATION FACTORY LAYER               │
│   (src/visualization/chart_factory.py, explorer.py)    │
│   Plotly Dark Graphite + Electric Violet/Cyan Theme    │
│   15+ chart types & Self-service Chart Explorer        │
└────────────────────────────────────────────────────────┘
```

---

## 2. Directory & Module Responsibilities

| Path | Purpose |
| :--- | :--- |
| `app.py` | Primary application entrypoint; configures theme, initializes session state, registers multipage navigation via `st.navigation`. |
| `pages/` | Step-by-step guided workflow pages (Step 1 Overview to Step 6 Reports). |
| `src/config.py` | Central configuration constants, color tokens, and the `STANDARD_BUSINESS_FIELDS` registry. |
| `src/data/loader.py` | Safe byte-level ingestion of CSV and Excel spreadsheets with automated multi-encoding fallback (`utf-8`, `latin-1`, `cp1252`). |
| `src/data/validation.py` | Non-destructive structural auditing (duplicate column deduplication, empty checks, missing headers). |
| `src/data/profiling.py` | Deep exploratory profiling (semantic type inference, missing cell percentages, cardinality, numeric quartiles, quality warnings). |
| `src/data/column_mapping.py` | Confidence-based column mapper (exact alias, normalized alias, token match, fuzzy similarity, ambiguity detection). |
| `src/data/canonical.py` | Canonical analytical data model, schema validation, capability checks, and conservative revenue/profit derivations. |
| `src/analytics/metrics.py` | Comprehensive Executive KPI calculation routines with full metadata, definitions, availability states, and edge-case protection. |
| `src/analytics/time_series.py` | Multi-frequency time-series resampling (Daily, Weekly, Monthly, Quarterly, Yearly), moving averages, PoP growth, and YoY tables. |
| `src/analytics/products.py` | Product rankings, Category performance rollups, and cumulative Pareto 80/20 concentration analysis. |
| `src/analytics/geography.py` | Territorial rollups across 4 geographic dimensions (Region, Country, State, City). |
| `src/analytics/customers.py` | Customer revenue ranking, concentration share (Top 5 / Top 10), and repeat vs. single-order retention metrics. |
| `src/analytics/profitability.py` | Negative-profit line item audit and 4-tier discount band segmentation (`0%`, `1-10%`, `11-20%`, `>20%`). |
| `src/analytics/statistics.py` | Descriptive statistical summary, Pearson/Spearman correlation matrices, and IQR outlier detection. |
| `src/analytics/filters.py` | Pure analytical multi-dimensional filtering engine (dates, categories, regions, transaction types). |
| `src/analytics/insights.py` | Deterministic, evidence-based commercial signals without external AI/LLM dependencies. |
| `src/visualization/themes.py` | Plotly theme registration adhering to the Dark Graphite, Electric Violet, and Cyan aesthetic. |
| `src/visualization/chart_factory.py` | Reusable, error-safe Plotly chart builders (15+ chart types: Line, Bar, Treemap, Waterfall, Funnel, 3D Scatter, etc.). |
| `src/visualization/explorer.py` | Interactive self-service Chart Explorer for custom ad-hoc visual queries. |
| `src/ui/layout.py` | CSS injection, branded header, live dataset telemetry banner, and footer. |
| `src/ui/components.py` | Glassmorphic metric cards, section headers, empty state holders, and step progress indicators. |
| `src/ui/filters.py` | Interactive sidebar dynamic filter control panel with live record counting. |
| `src/ui/navigation.py` | Guarded Previous/Next step navigation controller with validation gating. |
| `src/utils/formatting.py` | Formatting helpers for currency (USD, INR with Lakhs/Crores, EUR, GBP, JPY), percentages, and strings. |
| `src/utils/errors.py` | User-friendly error hierarchy concealing raw stack traces. |

---

## 3. Data Processing Lifecycle

1. **Ingestion & Safeguarding**:
   - The user selects a `.csv`, `.xlsx`, or `.xls` file (or clicks the sample data button).
   - `load_dataset()` validates file extension and size (capped at 50 MB).
   - In-memory bytes are probed through candidate encodings (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`).
   - The original raw DataFrame is stored intact in memory (`LoadedDataset.raw_df`).
2. **Structural Validation & Profiling**:
   - `validate_dataset()` sanitizes duplicate column headers with unambiguous suffixes (`Sales`, `Sales_1`) without altering raw data values.
   - `profile_dataset()` infers semantic data types (Datetime, Numeric, Categorical, ID, Free Text) and generates quality warnings (e.g. >30% missing values).
3. **Confidence-Based Column Mapping**:
   - `auto_detect_mappings()` compares detected column names against the 22 standard business field definitions in `src/config.py`.
   - Confidence scores range from 1.0 (exact alias) to 0.70 (token/fuzzy).
   - Conflicting or close-scored columns are flagged as `ambiguous` and presented to the user for explicit confirmation.
   - Essential fields (`sales` and `order_date`) are validated before advancing to analytics.
4. **Standardized Schema Generation**:
   - When confirmed, `create_standard_dataframe()` produces a normalized DataFrame with cleaned floats, parsed datetimes, and preserved unmapped attributes.

---

## 4. UI/UX & Design Conventions

- **Base Canvas**: Dark Graphite (`#0B0F19`) with elevated card surfaces (`#111827`, `#131B2E`).
- **Brand Accents**: Electric Violet (`#8B5CF6`) and Electric Cyan (`#06B6D4`).
- **Typography**: Google Fonts Inter and Outfit imported via CSS.
- **Micro-Interactions**: Glassmorphism, subtle hover card lifts, and status indicator pills.
- **Accessibility**: High-contrast text (`#F9FAFB`) exceeding WCAG AA standards.
