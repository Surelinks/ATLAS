# Atlas AI — Operational Intelligence & Incident Response Platform

> **Author:** Ezenwanne Kenneth  
> **Institution:** Capstone Project – MSSE66+  
> **Version:** 1.0.0 | **License:** MIT  
> **Live Demo:** https://atlas-ai-frontend.onrender.com  
> **API Docs:** https://atlas-ai-backend-bz3o.onrender.com/docs

---

## Overview

Atlas AI is an enterprise-grade AI platform designed for 330 kV / 132 kV power substation operations teams. It combines a **RAG-based SOP assistant**, real-time **SCADA telemetry simulation**, **incident root-cause analysis**, and **transformer DGA diagnostics** into a single, operator-facing web application.

**Value proposition:**  
*Help operations teams prevent procedural errors by surfacing the right SOP at the right moment, and resolve incidents faster through AI-driven root-cause analysis.*

---

## Key Features

| Module | Description |
|---|---|
| **Operations Copilot** | Upload PDF/DOCX SOPs; ask questions; get grounded, cited answers via RAG (Groq LLM + sentence-transformers) |
| **Real-time Dashboard** | Simulated 330 kV/132 kV SCADA telemetry – transformers, circuit breakers, busbars, alarms |
| **Incident Analyzer** | Event-timeline correlation, causal-chain analysis, root-cause report, search/filter/export |
| **System Analytics** | Trend charts, severity distribution, asset-level incident breakdowns, CSV export |
| **DGA Diagnostics** | IEC 60599-based dissolved-gas analysis for transformers T-401 and T-402 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                   │
│   Dashboard │ Ops Copilot │ Incident Analyzer │ Analytics│
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend (Python 3.11)           │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Ops Copilot │  │ Health / Ready│  │  (extensible) │  │
│  │  /api/v1/    │  │  /health      │  │               │  │
│  └──────┬───────┘  └──────────────┘  └───────────────┘  │
│         │                                                 │
│  ┌──────▼───────────────────────────────────────────┐    │
│  │               RAG Pipeline                        │    │
│  │  DocumentProcessor → SimpleVectorStore → LLMSvc  │    │
│  └──────────────────────────────────────────────────┘    │
│         │               │                                 │
│   tiktoken          sentence-transformers           Groq  │
│   (chunking)        (all-MiniLM-L6-v2)             (LLM) │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI 0.100+ (Python 3.11) | Async, auto-OpenAPI docs |
| LLM | Groq API — `llama-3.3-70b-versatile` | Free tier, ~2 s latency |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` | Local, no API key needed |
| Vector Store | `SimpleVectorStore` (NumPy + pickle) | In-memory, persisted to disk |
| Document Parsing | PyPDF2, python-docx, tiktoken | PDF, DOCX, TXT, MD |
| SCADA Simulator | `GridDataSimulator` (custom) | DNP3, PMU C37.118, DGA IEC 60599 |
| Frontend | Streamlit 1.30+ | React-inspired dark theme |
| Charts | Plotly | Interactive, exportable |
| CI/CD | GitHub Actions | Lint → test → security → build |
| Deployment | Render (free tier) | Backend + frontend as separate services |

---

## Project Structure

```
Atlas/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── health.py           # /health  /ready  (liveness + readiness probes)
│       │   └── ops_copilot.py      # /api/v1/ops-copilot/*
│       ├── core/
│       │   ├── config.py           # pydantic-settings – all env vars in one place
│       │   ├── exceptions.py       # Custom exception hierarchy + FastAPI handlers
│       │   └── middleware.py       # Request logging + X-Request-ID injection
│       ├── rag/
│       │   └── rag_service.py      # Retrieve → Generate → Cite pipeline
│       ├── services/
│       │   ├── document_processor.py  # PDF/DOCX extraction + token chunking
│       │   ├── llm_service.py         # Provider abstraction (Groq/OpenAI/Ollama)
│       │   ├── simple_vector_store.py # NumPy cosine-similarity vector store
│       │   └── scada_simulator.py     # GridDataSimulator (330 kV station)
│       └── main.py                 # FastAPI app factory, middleware, routers
├── ui/
│   └── app.py                      # Streamlit multi-page application
├── data/
│   ├── sops/                       # Sample SOP PDFs
│   └── incidents/                  # Sample incident JSON
├── docs/
│   ├── DECISIONS.md                # Architecture Decision Records (ADRs)
│   └── design-and-testing.md
├── .github/workflows/
│   ├── ci.yml                      # Full pipeline: lint, test, security, build
│   └── deploy-check.yml            # Quick validation on every push
├── render.yaml                     # Render deployment blueprint
├── runtime.txt                     # Python 3.11.9 (forces Render runtime)
├── requirements.txt
└── README.md
```

---

## Quick Start – Local Development

### Prerequisites

* Python 3.11 (3.12+ not recommended – some wheels are missing)
* A free [Groq API key](https://console.groq.com/keys)

### 1. Clone & set up environment

```bash
git clone https://github.com/Surelinks/ATLAS.git
cd ATLAS
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY=<your-key>
```

### 3. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 4. Start the frontend (new terminal)

```bash
streamlit run ui/app.py --server.port 8501
# UI: http://localhost:8501
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Active Groq model |
| `LLM_PROVIDER` | `groq` | `groq` \| `openai` \| `ollama` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model |
| `ENVIRONMENT` | `development` | `development` \| `production` |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS origins |
| `API_HOST` | `0.0.0.0` | Uvicorn bind address |
| `API_PORT` | `8000` | Uvicorn port |
| `VECTOR_DB_DIRECTORY` | `./vector_db` | Pickle persistence directory |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_BASE_URL` | `http://localhost:8000` | *(frontend only)* Backend URL |

---

## API Reference

Interactive docs are auto-generated by FastAPI:

* **Swagger UI:** `/docs`
* **ReDoc:** `/redoc`

### Core Endpoints

```
GET  /health                          Liveness probe
GET  /ready                           Readiness probe (checks vector store + LLM)
GET  /                                Service info

POST /api/v1/ops-copilot/query        Ask the Ops Copilot a question
POST /api/v1/ops-copilot/ingest       Upload an SOP document (PDF/DOCX/TXT/MD)
GET  /api/v1/ops-copilot/documents    List indexed documents
DELETE /api/v1/ops-copilot/documents/{id}  Remove a document
GET  /api/v1/ops-copilot/stats        Vector store statistics
```

---

## Deployment — Render

The `render.yaml` blueprint provisions two free-tier web services:

| Service | URL |
|---|---|
| Backend (FastAPI) | https://atlas-ai-backend-bz3o.onrender.com |
| Frontend (Streamlit) | https://atlas-ai-frontend.onrender.com |

### Required environment variables on Render

**Backend service:**

| Key | Value |
|---|---|
| `GROQ_API_KEY` | *your key* |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | `*` |

**Frontend service:**

| Key | Value |
|---|---|
| `API_BASE_URL` | `https://atlas-ai-backend-bz3o.onrender.com` |

---

## CI/CD Pipeline

Every push to `master` triggers GitHub Actions:

```
lint (black, isort, flake8)
  └─> test (pytest + coverage)
        └─> security (bandit, safety)
              └─> build (import validation)
                    └─> deploy-check (files verification)
```

Secrets required in GitHub → Settings → Secrets:

* `GROQ_API_KEY`

---

## SCADA Simulator

`GridDataSimulator` generates realistic telemetry for **330kV_Station_Alpha**:

| Asset | Type | Protocol |
|---|---|---|
| T-401 | Power Transformer (330/132 kV) | DNP3, DGA IEC 60599 |
| T-402 | Power Transformer (330/132 kV) | DNP3, DGA IEC 60599 |
| CB-101 | Circuit Breaker (330 kV) | DNP3 |
| CB-102 | Circuit Breaker (132 kV) | DNP3 |
| BUS-330 | 330 kV Busbar | ICCP, PMU C37.118 |
| BUS-132 | 132 kV Busbar | ICCP, PMU C37.118 |
| LINE-304 | Transmission Line | COMTRADE IEEE C37.111 |

---

## Testing

```bash
cd backend
pytest --cov=app --cov-report=html tests/
# HTML report: backend/htmlcov/index.html
```

---

## Sprint Timeline

| Sprint | Deliverable | Status |
|---|---|---|
| 1 | FastAPI scaffold, RAG pipeline, vector store | ✅ Complete |
| 2 | SCADA simulator, GridDataSimulator, 7 assets | ✅ Complete |
| 3 | Enterprise dark UI, React-style design system | ✅ Complete |
| 4 | Incident Analyzer, DGA diagnostics, Analytics | ✅ Complete |
| 5 | Middleware, exception handling, CI/CD | ✅ Complete |
| 6 | Render deployment, environment configuration | ✅ Complete |

---

## License

MIT © 2026 Ezenwanne Kenneth

## 🏗️ Architecture

### System Components

1. **Ops Copilot Module** (RAG-based SOP Enforcer)
   - Ingests SOPs, manuals, policies
   - Answers operational questions
   - Flags non-compliant actions
   - Explains procedure rationale

2. **Incident Analyzer Module** (Root Cause Engine)
   - Ingests incident logs (CSV/JSON/text)
   - Orders events into timelines
   - Detects anomaly patterns
   - Suggests probable root causes
   - Generates post-incident reports

3. **Unified Dashboard**
   - Metrics visualization
   - Alerts management
   - Audit trail

## 💻 Tech Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| Backend | FastAPI (Python 3.14) | ✅ Production Ready |
| AI/ML | Groq API (llama-3.3-70b), sentence-transformers | ✅ Implemented |
| Vector Store | SimpleVectorStore (in-memory + pickle) | ✅ Functional |
| SCADA Simulator | Custom GridDataSimulator (330kV/132kV) | ✅ Complete |
| Data Processing | Pandas, Pydantic | ✅ Implemented |
| Frontend | Streamlit 1.53 | ✅ React-style UI |
| Deployment | Render (recommended) | 🚀 Ready |
| Protocols | DNP3, Modbus, ICCP, COMTRADE, PMU, DGA | ✅ Simulated |

## 📂 Project Structure

```
atlas-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── rag/              # RAG pipeline components
│   │   ├── incident/         # Incident analysis logic
│   │   ├── models/           # Pydantic models
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Unit and integration tests
│   └── Dockerfile
│
├── ui/
│   └── streamlit_app.py      # Streamlit interface
│
├── data/
│   ├── sops/                 # Sample SOP documents
│   ├── incidents/            # Sample incident logs
│   └── proposals/            # Optional: consulting templates
│
├── docs/
│   ├── architecture.md       # System architecture
│   ├── design-and-testing.md # Design & testing document
│   └── DECISIONS.md          # Architecture decision records
│
├── .github/workflows/
│   └── ci.yml                # CI/CD pipeline
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## 📅 Sprint Timeline (12 Weeks)

### Sprint 1 (Weeks 1-4): Ops Copilot MVP ✅ COMPLETE
- [x] Project setup
- [x] SOP ingestion pipeline (PDF/DOCX/TXT)
- [x] Vector storage implementation (SimpleVectorStore)
- [x] RAG Q&A interface
- [x] Professional Streamlit UI with React-style design
- [x] Document upload functionality

### Sprint 2 (Weeks 5-8): Incident Analyzer ✅ COMPLETE
- [x] SCADA data simulation
- [x] Timeline builder with Plotly visualization
- [x] Root cause detection algorithms
- [x] DGA diagnostics (IEC 60599)
- [x] Incident correlation analysis

### Sprint 3 (Weeks 9-11): Platform Polish ✅ COMPLETE
- [x] Unified dashboard (4 modules)
- [x] System analytics with CSV export
- [x] React-inspired design system
- [x] Keyboard shortcuts & accessibility
- [x] Mobile responsive design
- [x] Production deployment guide
- [x] GitHub Actions CI/CD pipeline

### Final (Week 12): Documentation ✅ COMPLETE
- [x] Complete design & testing document
- [x] USER_GUIDE.md (500+ lines)
- [x] DEPLOYMENT_GUIDE.md (600+ lines)
- [x] TESTING_GUIDE.md (550+ lines)
- [x] API_DOCUMENTATION.md

## 🤖 AI Assistance Disclosure

This project was developed with AI assistance under human supervision:
- **ChatGPT**: Architecture design and documentation templates
- **DeepSeek**: Algorithm design and logical optimization
- **GitHub Copilot**: Code completion and boilerplate generation

All architectural decisions, code implementation, and final deliverables were reviewed, understood, and approved by the developer. The human developer maintains full understanding and accountability for all components.

## 📊 Data Source

All operational data (SOPs, incident logs) in this repository is synthetic and generated for demonstration purposes. No real utility data or proprietary information is included.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Groq API key (free at https://console.groq.com)
- Git

### Local Installation

```bash
# Clone the repository
git clone https://github.com/Surelinks/ATLAS.git
cd ATLAS

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run backend
cd backend
uvicorn app.main:app --port 8000 --reload

# Run frontend (in new terminal)
cd ..
streamlit run ui/app.py --server.port 8501
```

### Quick Access
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🚀 Deploy to Render

**Why Render?** Unlike Vercel (frontend-only), Render supports full-stack Python apps with persistent storage.

### Deploy Steps:

1. **Push to GitHub** (if not done already)
   ```bash
   git add .
   git commit -m "Production ready"
   git push origin master
   ```

2. **Create Render Account**: https://render.com

3. **Deploy Backend**:
   - New → Web Service
   - Connect GitHub repo
   - Name: `atlas-ai-backend`
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `GROQ_API_KEY`
   - Click "Create Web Service"

4. **Deploy Frontend**:
   - New → Web Service
   - Connect same repo
   - Name: `atlas-ai-frontend`
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0`
   - Add environment variable: `API_BASE_URL` → your backend URL
   - Click "Create Web Service"

5. **Test**: Visit your frontend URL and upload a document!

**See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions including Docker, AWS, and monitoring setup.**

## 📝 License

This is a capstone project for educational purposes.

## 👤 Author

Ezenwanne Kenneth
Quantic **MSSE66+ Capstone Project**  
Date: March 2026
