# Atlas AI: Operational Intelligence & Incident Response Platform

## 🎯 Project Overview

An AI-powered platform that helps operations teams prevent errors by enforcing SOPs and resolve incidents faster through AI-driven root cause analysis and automated reporting.

**One-Sentence Value Proposition:**  
Atlas AI helps operations teams prevent errors by enforcing SOPs and resolve incidents faster through AI-driven root cause analysis and automated reporting.

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

**MSSE66+ Capstone Project**  
Date: January 2026
