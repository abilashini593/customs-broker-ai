# Customs Broker AI 🚢📋

An AI-powered customs broker application designed to automate trade document extraction, container/seal validation, and deterministic compliance cross-checking.

---

## 🌟 Key Features

* **Vision-Powered Document Extraction:** Extracts structured metadata (commercial invoices, bills of lading, packing lists) including package counts, container numbers (`container_number`), and seal numbers (`seal_number`).
* **Deterministic Cross-Check Engine:** Validates extracted document data against compliance rules and shipment records in real-time.
* **Interactive UI Dashboard:** A modern frontend interface featuring live document previewing, extraction review, and a **Re-validate** workflow.
* **Audit Trail & Logging:** Tracks validation events and modifications to ensure customs clearance compliance.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, SQLAlchemy, SQLite/PostgreSQL, Google Gemini API
* **Frontend:** Next.js, Tailwind CSS
* **Utilities & Tooling:** Pydantic, Pytest, Docker

---

## 📁 Project Structure

```text
customs-broker-ai/
│
├── backend/                  # FastAPI backend service
│   ├── app/
│   │   ├── api/              # API routers (shipments, cross_check, documents, export)
│   │   ├── core/             # Configuration, database setup
│   │   ├── services/         # Extraction & cross-check business logic
│   │   └── models/           # SQLAlchemy database models
│   ├── uploads/              # Local document storage
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Next.js frontend dashboard
│   ├── app/                  # App router pages & components
│   └── package.json          # Node dependencies
│
├── .gitignore                # Git ignore configuration
├── deployment.md             # Deployment instructions
└── README.md                 # Project documentation
⚙️ Getting Started Locally
1. Clone the Repository

git clone [https://github.com/abilashini593/customs-broker-ai.git](https://github.com/abilashini593/customs-broker-ai.git)
cd customs-broker-ai

2. Set Up the Backend

cd backend
python -m venv venv
# Activate virtual environment:
# On Windows (PowerShell):
.\venv\Scripts\Activate
# On Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt

Create a .env file inside the backend/ directory and add your environment variables:
PROJECT_NAME="Customs Broker AI"
API_V1_STR="/api/v1"
GEMINI_API_KEY="your-gemini-api-key-here"

Start the FastAPI server:
python start_backend.py

3. Set Up the Frontend
Open a new terminal window, navigate to the frontend directory, install dependencies, and start the development server:

cd frontend
npm install
npm run dev
(Frontend runs by default at http://localhost:3000)

🚀 API Endpoints Overview
GET /api/v1/shipments — Retrieve all active shipments and status.

POST /api/v1/cross-check/shipments/{shipment_id}/revalidate — Trigger re-validation engine for container, seal, and package data.

GET /docs — Interactive Swagger documentation for testing API endpoints directly.
