# 📈 Sales Analytics Dashboard

> **Understand Sales. Discover Trends. Make Better Decisions.**

An interactive sales intelligence workspace built with **Python**, **Streamlit**, and **Plotly** that transforms raw sales data into actionable commercial insights and visual reports.

---

## 🌟 Project Overview

The **Sales Analytics Dashboard** is engineered to help business owners, sales executives, and analysts understand commercial health without relying on rigid CSV templates or proprietary schemas. It accepts multi-format sales spreadsheets (CSV, XLSX, XLS), profiles structural data quality, aligns diverse column aliases using confidence-based matching, and prepares data for multi-dimensional revenue and margin analysis.

### What the Application Answers:
- **Revenue Drivers**: How much revenue the business generates and transaction volume.
- **Profitability & Margins**: How discounts impact gross margins and where net loss occurs.
- **Assortment Performance**: Which product categories and lines contribute the majority of revenue.
- **Geographic Dynamics**: Which regions, states, and cities represent primary markets.
- **Data Health**: What missing values, duplicate transactions, or formatting anomalies exist in the data.

---

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11 – 3.13 | Core programming runtime |
| **Web Framework** | Streamlit | 1.49.1 | Interactive web application and multipage routing |
| **Data Processing** | Pandas & NumPy | 2.3.2 / 2.3.3 | In-memory data manipulation, profiling, and aggregations |
| **Spreadsheet Engine** | OpenPyXL | 3.1.5 | Microsoft Excel (.xlsx) file parsing |
| **Visualizations** | Plotly | 6.3.0 | Custom-themed dark interactive charts |
| **Statistics** | SciPy | 1.16.2 | Advanced distribution analysis |
| **Testing** | Pytest | 8.4.2 | Automated unit and integration testing suite |
| **Code Quality** | Ruff | 0.16.2 | Fast Python linting and code formatting |
| **CI / Automation** | GitHub Actions | Ubuntu Latest | Continuous integration workflow across Python 3.11-3.13 |

---

## 🗺️ Implementation Status: Master Prompt 1 of 3

This project is developed across three sequential phases:

- [x] **Phase 1: Foundation, Architecture, UI/UX, and Data Ingestion (COMPLETED)**
  - Modular project architecture and directory structure.
  - Dark Graphite, Electric Violet, and Cyan design system with responsive CSS.
  - Streamlit `st.navigation` multipage flow with state-preserving Previous / Next controls.
  - Robust file loader supporting CSV, XLSX, encoding fallbacks (`utf-8`, `latin-1`, `cp1252`), and size caps (50 MB).
  - In-depth dataset profiling (semantic type inference, quartiles, missing cell rates, quality warnings).
  - Confidence-based column mapping system with 22 standard business fields, alias detection, and manual overrides.
  - Bundled 150-record Superstore sample dataset with 1-click loading.
  - Plotly dark theme registration and chart factory.
  - Comprehensive automated test suite (**21 passed, 0 errors**).
- [ ] **Phase 2: Analytics Engine (Planned for Master Prompt 2)**
  - Advanced multi-dimensional filtering (date range picker, category, region, customer segment).
  - Pareto 80/20 customer concentration analysis.
  - Discount vs. Margin erosion sensitivity analysis.
  - Geographic choropleth maps and regional breakdown.
  - Automated natural language insights engine.
- [ ] **Phase 3: Finalization & Deployment (Planned for Master Prompt 3)**
  - Executive PDF report export engine.
  - Performance benchmarking for large files.
  - Accessibility audit and Streamlit Community Cloud deployment.

---

## 📂 Project Structure

```
sales-analytics-dashboard/
│
├── app.py                      # Main entrypoint and navigation router
├── requirements.txt            # Pinned production dependencies
├── pyproject.toml              # Ruff and Pytest configuration
├── README.md                   # Complete project documentation
├── .gitignore                  # Git tracking rules
│
├── .streamlit/
│   └── config.toml             # Streamlit dark theme & server settings
│
├── assets/
│   ├── README.md
│   └── styles.css              # Custom CSS design system
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, UI tokens, and 22 standard fields
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py           # Ingestion and multi-encoding CSV/Excel reader
│   │   ├── validation.py       # Structural checks and header sanitization
│   │   ├── profiling.py        # Semantic inference and exploratory audit
│   │   └── column_mapping.py   # Confidence-based business field mapper
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Foundational KPIs (Sales, Orders, AOV, Profit)
│   │   ├── aggregations.py     # Time-series and categorical aggregations
│   │   └── insights.py         # Rule-based commercial signals
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── chart_factory.py    # Reusable Plotly chart builders
│   │   └── themes.py           # Plotly Dark Graphite / Violet / Cyan template
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── layout.py           # Header, live status banner, and footer
│   │   ├── components.py       # Metric cards, step indicators, alert boxes
│   │   └── navigation.py       # Session state management and guarded steps
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatting.py       # Currency, percentages, and string normalization
│       └── errors.py           # User-safe error hierarchy
│
├── pages/
│   ├── README.md
│   ├── 1_Overview.py           # Step 1: Welcome & sample dataset loader
│   ├── 2_Upload_Data.py        # Step 2: Upload interface & file validation
│   ├── 3_Data_Inspection.py    # Step 3: Data health audit & profiling
│   ├── 4_Column_Mapping.py     # Step 4: Schema mapping & alignment
│   ├── 5_Analysis_Workspace.py # Step 5: Foundational KPIs & charts
│   └── 6_Reports_and_Export.py # Step 6: CSV & JSON telemetry export
│
├── data/
│   ├── README.md               # Data privacy notes
│   └── samples/
│       ├── README.md           # Dataset sources & attribution
│       └── superstore_sample.csv # Bundled 150-record sample dataset
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Synthetic test fixtures
│   ├── test_loader.py          # Ingestion & encoding tests
│   ├── test_validation.py      # Structural validation tests
│   ├── test_profiling.py       # Statistical profiling tests
│   ├── test_column_mapping.py  # Column mapping & alias tests
│   └── test_metrics.py         # KPI and aggregation tests
│
├── docs/
│   ├── architecture.md         # Architecture and lifecycle design
│   ├── data_dictionary.md      # 22 standard field definitions and aliases
│   └── testing_checklist.md    # Quality assurance and test verification matrix
│
└── .github/
    └── workflows/
        └── tests.yml           # GitHub Actions CI workflow
```

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- Git installed.

### 2. Clone or Enter Project
```bash
cd sales-analytics-dashboard
```

### 3. (Optional) Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Automated Test Suite

Run the full Pytest suite:
```bash
pytest -v
```

Run code quality linting:
```bash
ruff check .
```

---

## 🔒 Data Privacy & Security Guardrails

- **Zero External API Calls**: The application does not transmit uploaded datasets to OpenAI, cloud storage, or external LLM APIs.
- **In-Memory Processing**: Uploaded files exist solely in memory during the active session.
- **No Evaluation of Untrusted Code**: Strictly avoids `eval()`, `exec()`, or untrusted Python `pickle` deserialization.
- **Sanitized Upload Boundaries**: Validates MIME types, extensions (`.csv`, `.xlsx`, `.xls`), and caps uploads at 50 MB.
- **Git Exclusions**: `.gitignore` strictly excludes `data/uploads/`, `.env` files, credentials, and temporary working copies.
