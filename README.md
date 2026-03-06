# IntelliCost: Procurement Cost Intelligence for HPCL Purchase Orders

## 1. Project Overview
IntelliCost is a multi-stage procurement intelligence system designed to convert unstructured HPCL Purchase Orders (POs) into standardized, analytics-ready cost intelligence.

The project addresses a core industry issue: the same material often appears in multiple textual forms across purchase records, making item-level historical cost analysis unreliable. IntelliCost resolves this through item standardization, canonical coding, vendor comparison, forecasting, anomaly detection, and an interactive dashboard.

This repository currently contains:
- Stage 1 assets as independent notebooks (`stage1/`)
- Integrated Stage 2, Stage 3, and Stage 4 code (deployed Streamlit app)

## 2. Business Problem
Procurement teams typically have large volumes of PO data but limited decision-ready intelligence due to:
- inconsistent item descriptions
- absence of stable item identity
- fragmented historical price tracking
- difficult vendor and region-level comparisons
- delayed risk detection for unusual pricing behavior

Example of the same item represented differently:
- `CS Pipe 100 mm`
- `Carbon Steel Pipe of 100 mm diameter`
- `CS pipeline 100mm SCH40`

## 3. End-to-End Solution Stages
### Stage 1: PO Digitization and Structuring (Independent notebooks)
1. PDF to high-resolution images
2. Layout-aware OCR to raw JSON
3. JSON normalization to structured JSON and spreadsheet-ready outputs

### Stage 2: Intelligent Item Standardization
1. Raw text normalization with domain mappings
2. Semantic matching using embeddings + vector search
3. Canonical item code linking (or new code creation when required)

### Stage 3: Cost and Risk Intelligence
1. Historical item-level cost repository preparation
2. Time-series forecasting for planning and budgeting
3. Anomaly detection for pricing risk visibility

### Stage 4: Unified Decision Dashboard
1. Item-centric analytics interface
2. Vendor and trend visualization
3. Risk and anomaly monitoring view

## 4. Repository Scope and Structure
```text
newf/
+-- api/
¦   +-- main.py
¦   +-- synthetic_hpcl_po_data.csv
+-- core/
¦   +-- analytics.py
¦   +-- anomaly.py
¦   +-- data_loader.py
¦   +-- item_master.py
¦   +-- item_master.csv
¦   +-- item_index.faiss
¦   +-- repository.py
¦   +-- vendor_comparison.py
+-- dashboard/
¦   +-- app.py
+-- stage1/
¦   +-- stage-1-1.ipynb
¦   +-- stage-1-2-1-3.ipynb
+-- synthetic_hpcl_po_data.csv
+-- requirements.txt
+-- runtime.txt
+-- Coders.pdf
```

Notes:
- `dashboard/app.py` is the primary deployed interface for Stage 2/3/4.
- `stage1/` notebooks are independent execution assets (prepared in a Kaggle-style workflow).

## 5. Technology Stack
### Core Data and Analytics
- Python
- pandas, numpy
- statsmodels (ARIMA forecasting)

### Item Standardization
- sentence-transformers (`all-MiniLM-L6-v2`)
- FAISS (`faiss-cpu`) for semantic similarity search
- rule-based normalization and numeric-attribute safety checks

### Application and Deployment
- Streamlit (interactive dashboard)
- FastAPI and Uvicorn are present in dependencies for service-oriented extension paths
- Streamlit Community Cloud deployment (`runtime.txt` + `requirements.txt`)

## 6. Data Inputs
Primary dataset file used by dashboard:
- `synthetic_hpcl_po_data.csv`

Expected columns include:
- `po_id`
- `item_description`
- `vendor`
- `region`
- `department`
- `po_date`
- `quantity`
- `unit_price`
- `po_value`

## 7. Local Setup and Execution
### Prerequisites
- Python 3.11 recommended
- pip

### Installation
```bash
pip install -r requirements.txt
```

### Run Dashboard (Stage 2/3/4)
```bash
streamlit run dashboard/app.py
```

The dashboard provides:
- historical price trend view
- vendor-wise comparison
- short-horizon forecast output
- anomaly detection table
- sidebar-based item standardization lookup

## 8. Streamlit Cloud Deployment
This repository is configured for Streamlit Cloud deployment.

Required files already present:
- `requirements.txt`
- `runtime.txt` (Python runtime pin)

Deployment configuration:
- Repository: `kumarayush0104/HPCL_Coders`
- Branch: `main`
- Main file path: `dashboard/app.py`
- Live application: `https://hpcl-coders.streamlit.app/`

## 9. Stage 1 Execution Notes
Stage 1 notebook assets are in `stage1/` and represent:
- high-resolution PDF page rendering
- layout-aware OCR extraction
- raw-to-structured procurement record transformation

These notebooks were prepared for notebook-first execution and include references to Kaggle paths and packages.

## 10. Module-Level Functional Map
- `core/data_loader.py`: data loading and item-code preparation
- `core/item_master.py`: text normalization, embedding generation, FAISS matching, canonical assignment
- `core/repository.py`: item-level time-series aggregation
- `core/analytics.py`: ARIMA-based forecasting
- `core/anomaly.py`: z-score anomaly detection
- `core/vendor_comparison.py`: vendor-level comparative analytics
- `dashboard/app.py`: unified interactive interface

## 11. Assumptions and Current Constraints
- historical data in current repo is synthetic for confidentiality-safe validation
- Stage 1 and Stage 2/3/4 are currently decoupled in execution
- real production behavior should be revalidated on actual HPCL procurement data and noise patterns

## 12. Planned Enhancements
- direct Stage 1 to Stage 2/3/4 automated pipeline handoff
- dynamic thresholding for semantic matching confidence by item class
- richer attribute/context inference (department/project/region)
- audit and compliance-oriented traceable reporting outputs
- large-scale validation on real operational procurement streams

## 13. References
- HPCL Annual Report (2024-25)
- Scribd PO samples and work-order references
- GeM procurement document references
- Hugging Face OCR and Transformers documentation
- FAISS documentation and vector search literature

## 14. Ownership
Developed by Team CODERS as part of Challenge 3.3: Creating Intelligent Cost Database.

## 15. Contributors
Contributors:
- Ankita Kumari
- Shyam Kumar
- Prateek Yadav

Mentor:
- Alakh Avasthi

