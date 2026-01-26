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

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Backend | FastAPI (Python) | Async, easy docs, great for ML/AI |
| AI/ML | OpenAI GPT-4, LangChain, ChromaDB | RAG, reasoning, embeddings |
| Data Processing | Pandas, Pydantic | Clean data handling |
| Database | PostgreSQL + pgvector / ChromaDB | Hybrid relational + vector search |
| Frontend | Streamlit | Quick UI for demo |
| CI/CD | GitHub Actions | Automated testing/deployment |
| Deployment | Docker + Railway/Render | Free tier, scalable |

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

### Sprint 1 (Weeks 1-4): Ops Copilot MVP
- [x] Project setup
- [ ] SOP ingestion pipeline
- [ ] Vector storage implementation
- [ ] RAG Q&A interface
- [ ] Basic Streamlit UI
- [ ] Demo recording #1

### Sprint 2 (Weeks 5-8): Incident Analyzer
- [ ] Log ingestion
- [ ] Timeline builder
- [ ] Root cause reasoning
- [ ] Report generator
- [ ] Demo recording #2

### Sprint 3 (Weeks 9-11): Platform Polish
- [ ] Unified dashboard
- [ ] Audit trail
- [ ] Authentication
- [ ] CI/CD pipeline
- [ ] Deployment
- [ ] Final demo recording

### Final (Week 12): Documentation & Submission
- [ ] Complete design & testing document
- [ ] Final video demo
- [ ] Submission preparation

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
- OpenAI API key
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd atlas-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
cd backend
uvicorn app.main:app --reload
```

## 📝 License

This is a capstone project for educational purposes.

## 👤 Author

**MSSE66+ Capstone Project**  
Date: January 2026
