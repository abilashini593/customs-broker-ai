# Deployment & Operations Guide
## Project 1: Customs Broker's AI Document Extraction & Cross-Check Tool
**Platform:** ClearBorder AI Enterprise (v4.2)  
**Date:** 2026-11-02  

---

### 1. Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.10+ (Tested on Python 3.11.9)
- **Node.js:** 18+ or 20+ (Tested on Node.js v24.21.0)
- **Package Managers:** `pip` and `npm`

---

### 2. Project Directory Structure
```
customs-broker-ai/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers (shipments, cross_check, documents, export, audit)
│   │   ├── core/            # Config, settings, and database session setup
│   │   ├── models/          # Relational SQLAlchemy models (Shipments, ExtractedFields, etc.)
│   │   ├── schemas/         # Pydantic v2 schemas and validation contracts
│   │   ├── services/        # CrossCheckEngine, VisionExtractor, CustomsExporter, SeedData
│   │   └── main.py          # Application entrypoint & CORS middleware
│   ├── tests/
│   │   └── test_cross_check.py # Automated unit test suite (10/10 passing tests)
│   ├── requirements.txt     # Python backend dependencies
│   └── customs_broker.db    # SQLite database (auto-seeded on first launch)
├── frontend/
│   ├── app/                 # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/          # 6 Production Screens & Modular UI Components
│   ├── lib/                 # Typed API client with live FastAPI connectivity & fallback
│   ├── package.json         # Frontend configuration
│   └── tailwind.config.js   # Enterprise dark-mode palette (#09090b)
├── bin/                     # Local toolchain launcher scripts (node.cmd, npm.cmd)
├── start_backend.py         # 1-Click Python backend server launcher
├── start_frontend.bat       # 1-Click Frontend launcher
├── TDD.md                   # Complete Technical Design Document
└── deployment.md            # This operational guide
```

---

### 3. Step-by-Step Local Setup & Execution

#### Option A: Quick-Start Backend (FastAPI)
Open a terminal in the project root:
```powershell
# 1. Navigate to backend directory
cd backend

# 2. (Optional) Activate your Python virtual environment if using one:
# python -m venv venv
# .\venv\Scripts\Activate.ps1

# 3. Install dependencies:
pip install -r requirements.txt

# 4. Run the FastAPI development server:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API URL:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/health`

*(Note: The backend automatically seeds 4 realistic customs shipments with line items, weights, and cross-checks on initial startup!)*

#### Option B: Quick-Start Frontend (Next.js)
Open a second terminal in the project root:
```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Run the Next.js development server:
npm run dev
# or: npx next dev -p 3000
```
- **Frontend Web Application:** `http://localhost:3000`

---

### 4. Running the Automated Unit Test Suite
To verify all deterministic business rules, weight-matching tolerances, and manager override logic:
```powershell
cd backend
$env:PYTHONPATH = (Get-Location).Path
python -m pytest tests/test_cross_check.py -v
```
**Expected Test Output:**
```
tests/test_cross_check.py::TestCrossCheckEngine::test_line_items_sum_exact_match PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_line_items_sum_mismatch_fails_and_blocks PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_line_items_rounding_tolerance_passes PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_gross_weight_matching_exact PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_gross_weight_mismatch_fails_and_blocks PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_gross_weight_within_tolerance_passes PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_manager_override_unblocks_rule PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_consignee_entity_matching PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_consignee_mismatch_blocks_export PASSED
tests/test_cross_check.py::TestCrossCheckEngine::test_hsn_code_validation_success_and_failure PASSED
======================= 10 passed in 1.09s =======================
```

---

### 5. Environment Variables Reference
No secret keys are required to run the local application in full fidelity.

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./customs_broker.db` | Relational database connection string. Set to `postgresql://user:pass@host/db` for PostgreSQL. |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000/api` | Base URL used by the Next.js frontend to communicate with the FastAPI backend. |
| `WEIGHT_TOLERANCE_KG` | `5.0` | Maximum absolute allowable weight discrepancy (in kilograms). |
| `WEIGHT_TOLERANCE_PERCENT` | `0.5` | Maximum percentage allowable weight discrepancy (0.5%). |
| `AMOUNT_TOLERANCE_CURRENCY` | `0.10` | Allowable rounding difference between line items sum and invoice total ($0.10). |
| `CONFIDENCE_THRESHOLD` | `85.0` | OCR fields with confidence score below this threshold receive an amber warning badge. |

---

### 6. Reviewer Demo Accounts & Testing Guide

The application features an interactive **Role Switcher** directly in the top navigation bar. No manual credentials are required; reviewers can switch roles seamlessly:

#### Persona 1: Documentation Executive (`John Doe`)
- **Focus:** Daily OCR document ingestion and field verification.
- **Workflow to test:**
  1. Open Shipment `#SHP-2026-8942` (Shenzhen Precision Microelectronics).
  2. Notice the amber badge on **Item #1 HSN Code (78.2% Conf)** and **Carrier Seal No (79.4% Conf)**.
  3. Click the amber **"Confirm"** button: observe instant verification, transition to green status pill, and automated audit logging.
  4. Note that the **Export Customs Filing** button remains locked because of the critical weight mismatch between the carrier BL and the packing list.

#### Persona 2: Documentation Manager (`Sarah Chen`)
- **Focus:** Compliance sign-off, authorized discrepancy overrides, and final customs filing export.
- **Workflow to test:**
  1. Click **"Doc Manager"** in the top navigation bar.
  2. In the **Deterministic Cross-Check Engine** card for `#SHP-2026-8942`, notice the red callout on `RULE_GROSS_WEIGHT_CONSISTENCY` (+350 kg variance).
  3. Click **"Override Blocker"**: enter an audit justification (e.g. *"Tare weight of 4 heavy-duty steel pallets included on carrier scale certificate"*).
  4. Click **"Authorize & Sign Off"**: observe the status pill transition to `OVERRIDDEN` and the shipment status change to `Cleared`.
  5. The **"Export Customs Filing (EDI)"** button is now unlocked! Click it to preview the exact ICEGATE / Single Window declaration layout and download the final CSV manifest.
  6. Click **"Audit Logs"** in the top bar to inspect the immutable chronological audit ledger.
