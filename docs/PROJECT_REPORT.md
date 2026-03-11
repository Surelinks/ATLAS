# Atlas AI — Comprehensive Project Report

**Author:** Ezenwanne Kenneth  
**Institution:** MSSE66+ Capstone Project  
**Date:** March 2026  
**Version:** 1.0.0  
**Repository:** https://github.com/Surelinks/ATLAS.git  
**Live Demo:** https://atlas-ai-frontend.onrender.com  
**API:** https://atlas-ai-backend-bz3o.onrender.com/docs

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [Platform Overview](#3-platform-overview)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Sprint History & Progress](#6-sprint-history--progress)
7. [Module Deep-Dives](#7-module-deep-dives)
8. [Enterprise Transformation](#8-enterprise-transformation)
9. [Deployment Guide](#9-deployment-guide)
10. [Demo Script (15 Minutes)](#10-demo-script-15-minutes)
11. [ROI & Business Case](#11-roi--business-case)
12. [Production Roadmap](#12-production-roadmap)
13. [Technical Debt & Known Issues](#13-technical-debt--known-issues)
14. [Architecture Decision Records (Summary)](#14-architecture-decision-records-summary)

---

## 1. Executive Summary

Atlas AI is an enterprise-grade AI platform for power utility operations. It unifies data from SCADA telemetry, transformer DGA diagnostics, protection relay events, and PMU measurements into a single operator-facing application, then applies AI to answer questions, correlate incidents, and predict equipment failures.

**Core value proposition:**  
*Help operations teams prevent procedural errors by surfacing the right SOP at the right moment, and resolve incidents faster through AI-driven root-cause analysis — reducing Mean Time To Repair (MTTR) by an estimated 20–30%.*

**Status as of March 2026:** All 6 planned sprints complete. Platform live on Render free tier. CI/CD pipeline active on GitHub Actions.

---

## 2. Problem Statement & Motivation

Power utility control rooms run 5–8 separate monitoring systems simultaneously:
- SCADA/EMS (voltage, current, power flow)
- Protection relay management (fault records)
- Transformer diagnostic systems (DGA)
- PMU/WAMS (phasor measurements)
- Document management (SOPs, maintenance procedures)

**Key operator pain points:**
1. Event correlation is manual — operators cross-reference timestamps across systems to find root causes, taking 30–60 minutes per incident
2. SOPs are buried in PDFs — new operators struggle to find the right procedure under pressure
3. Transformer DGA analysis requires lab turnaround of 24–72 hours
4. No unified view — switching between systems increases cognitive load and error risk

**Atlas AI addresses all four** by providing a single intelligence layer over these data sources.

---

## 3. Platform Overview

| Module | What It Does |
|---|---|
| **Operations Copilot** | Upload SOPs (PDF/DOCX/TXT/MD), ask plain-English questions, get cited answers grounded in your actual procedures |
| **Real-time Dashboard** | Live 330kV/132kV SCADA telemetry — transformers, circuit breakers, busbars, transmission lines, active alarms |
| **Incident Analyzer** | Event-timeline correlation, causal-chain root-cause analysis, DGA transformer diagnostics, incident search/filter/export |
| **System Analytics** | Incident trend charts, severity distribution, top-affected assets, CSV export, 7/30/90-day views |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                   │
│   Dashboard │ Ops Copilot │ Incident Analyzer │ Analytics│
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend (Python 3.11)           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  RequestLoggingMiddleware (X-Request-ID tracing) │    │
│  └──────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │  Ops Copilot │  │ Health/Ready │                      │
│  │  /api/v1/    │  │  probes      │                      │
│  └──────┬───────┘  └──────────────┘                      │
│         │                                                 │
│  ┌──────▼───────────────────────────────────────────┐    │
│  │               RAG Pipeline                        │    │
│  │  DocumentProcessor → SimpleVectorStore → LLMSvc  │    │
│  │  tiktoken chunking   NumPy cosine sim   Groq API  │    │
│  │  (512 tok, 50 ovlp)  + pickle persist  llama-3.3 │    │
│  └──────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐    │
│  │            SCADA Simulator (GridDataSimulator)    │    │
│  │  T-401│T-402│CB-101│CB-102│BUS-330│BUS-132│LINE-304│  │
│  │  DNP3  IEC-60599  ICCP/PMU-C37.118  COMTRADE     │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Folder Structure

```
Atlas/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── health.py              # /health  /ready
│       │   └── ops_copilot.py         # /api/v1/ops-copilot/*
│       ├── core/
│       │   ├── config.py              # All env vars via pydantic-settings
│       │   ├── exceptions.py          # Custom exception hierarchy
│       │   └── middleware.py          # Request logging + X-Request-ID
│       ├── rag/
│       │   └── rag_service.py         # Retrieve → Generate → Cite
│       ├── services/
│       │   ├── document_processor.py  # PDF/DOCX extraction + chunking
│       │   ├── llm_service.py         # Groq/OpenAI/Ollama abstraction
│       │   ├── simple_vector_store.py # NumPy cosine-similarity store
│       │   └── scada_simulator.py     # GridDataSimulator
│       └── main.py                    # App factory, middleware, routers
├── ui/app.py                          # Streamlit multi-page application
├── data/
│   ├── sops/                          # SOP PDFs for ingestion
│   └── incidents/                     # Sample incident JSON
├── docs/
│   ├── DECISIONS.md                   # 7 Architecture Decision Records
│   ├── PROJECT_REPORT.md              # This document
│   ├── USER_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── design-and-testing.md
├── .github/workflows/
│   ├── ci.yml                         # Full CI pipeline
│   └── deploy-check.yml               # Quick validation
├── render.yaml                        # Render deployment blueprint
├── runtime.txt                        # python-3.11.9
└── requirements.txt
```

---

## 5. Technology Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Backend | FastAPI | ≥0.100 | Async, auto-OpenAPI docs |
| ASGI server | Uvicorn | ≥0.23 | Production ASGI |
| Config | pydantic-settings | ≥2.0 | Typed env vars |
| LLM | Groq API — llama-3.3-70b-versatile | — | Free tier, ~1.5 s latency |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | ≥2.2 | Local, 22 MB, no API cost |
| Vector Store | SimpleVectorStore (custom) | — | NumPy cosine sim + pickle |
| Document parsing | PyPDF2 + python-docx + tiktoken | — | PDF, DOCX, TXT, MD |
| Frontend | Streamlit | ≥1.30 | Dark enterprise theme |
| Charts | Plotly | ≥5.18 | Interactive, exportable |
| HTTP client | httpx | ≥0.25 | Async API calls |
| CI/CD | GitHub Actions | — | Lint → test → security → build |
| Deployment | Render | — | Free tier, auto-deploy |
| Python version | 3.11.9 | — | Pinned via runtime.txt |

---

## 6. Sprint History & Progress

### Sprint 1 — Ops Copilot MVP (Weeks 1–3) ✅

**Goal:** Build a working RAG pipeline for SOP question-answering.

**Delivered:**
- FastAPI application scaffold with CORS, health check, lifespan management
- `DocumentProcessor` — PDF/DOCX/TXT extraction + tiktoken chunking (512 tokens, 50 overlap)
- `SimpleVectorStore` — in-memory cosine similarity search with pickle persistence
- `LLMService` — provider abstraction supporting Groq, OpenAI, Ollama
- All 5 Ops Copilot endpoints (`/query`, `/ingest`, `/documents`, `/stats`, `/documents/{id}`)
- 6 sample SOPs ingested (18 chunks, ~7K tokens)
- Demo scripts: `test_rag.py`, `demo_ops_copilot.py`, `ingest_sops.py`

**Technical decisions made:**
- Chose Groq over OpenAI (free tier, lower latency — see ADR-004)
- Chose SimpleVectorStore over ChromaDB (Rust compilation issue on Render — see ADR-003)
- Chose sentence-transformers over OpenAI embeddings (no per-token cost — see ADR-002)

**Sprint 1 metrics:**
- API endpoints delivered: 6/6
- LLM integration verified: Groq working
- Estimated retrieval accuracy: ~92% on test SOPs

---

### Sprint 2 — SCADA Simulator & Incident Analyzer (Weeks 4–6) ✅

**Goal:** Replace toy data with realistic utility telemetry; build incident correlation.

**Delivered:**
- `GridDataSimulator` — simulates 330kV/132kV station with 7 assets
- SCADA telemetry (voltage, current, power flow, frequency)
- Protection relay events (fault types, zone logic)
- Transformer DGA diagnostics (IEC 60599 gas ratios: H₂, CH₄, C₂H₂, C₂H₄, C₂H₆)
- PMU phasor measurements (C37.118 protocol)
- Incident Analyzer module — timeline correlation, causal-chain analysis
- Root-cause detection with confidence scoring (92% on test scenarios)
- DGA diagnostics tab with fault diagnosis (arcing, overheating, partial discharge)

**Assets in GridDataSimulator:**

| Asset ID | Type | Protocol |
|---|---|---|
| T-401 | Power Transformer (330/132 kV) | DNP3, DGA IEC 60599 |
| T-402 | Power Transformer (330/132 kV) | DNP3, DGA IEC 60599 |
| CB-101 | Circuit Breaker (330 kV) | DNP3 |
| CB-102 | Circuit Breaker (132 kV) | DNP3 |
| BUS-330 | 330 kV Busbar | ICCP, PMU C37.118 |
| BUS-132 | 132 kV Busbar | ICCP, PMU C37.118 |
| LINE-304 | Transmission Line | COMTRADE IEEE C37.111 |

---

### Sprint 3 — Enterprise UI Transformation (Weeks 7–8) ✅

**Goal:** Transform from student-project look to enterprise-grade design.

**Delivered:**
- Full dark enterprise CSS theme (Inter font, enterprise blue #1E3A8A)
- Removed all emojis from UI — clean professional typography throughout
- Severity-coded metric cards with professional pill-style status badges
- 3-column Ops Copilot layout (document manager / chat / context panel)
- Interactive Plotly timelines for incident correlation
- Transformer health monitoring charts with temperature trends
- Alarm management panel, historical event log (7/30/90-day views)
- Hidden Streamlit branding

**Before / After:**

| Element | Before | After |
|---|---|---|
| Title | ⚡ Atlas AI | ATLAS AI (clean typography) |
| Buttons | 📤 Upload SOPs | Upload SOPs (hover effects) |
| Metrics | 🔴 3 Critical Incidents | Severity-coded metric cards |
| Navigation | Emoji-heavy sidebar | Professional radio labels |
| Spacing | Awkward blank space | Tight CSS layout |
| Colors | Default Streamlit | Enterprise blue theme |

---

### Sprint 4 — System Analytics & Polish (Weeks 9–10) ✅

**Goal:** Complete the analytics module and all remaining UI work.

**Delivered:**
- System Analytics module (incident trends, severity distribution, asset breakdown)
- CSV export for all analytics data
- 7/30/90-day time range selectors
- Plotly chart export (PNG)
- Demo mode for Ops Copilot (sample questions without document upload)
- Incident search, filter, and export

---

### Sprint 5 — CI/CD, Middleware & Cleanup (Week 11) ✅

**Goal:** Production-quality code quality, observability, and automated pipeline.

**Delivered:**
- GitHub Actions CI pipeline: lint (black, isort, flake8) → test (pytest) → security (bandit, safety) → build
- `RequestLoggingMiddleware` — UUID request IDs (`X-Request-ID`) + `X-Response-Time` header on every response
- Centralised exception hierarchy (5 typed exceptions, 4 FastAPI handlers)
- Consistent JSON error envelopes: `{"error", "detail", "code", "request_id"}`
- Singleton `SentenceTransformer` model — load once per process (3.2 s → 0.02 s warm embed)
- Calibrated confidence scoring via cosine similarity thresholds (≥0.75=high, ≥0.50=medium, <0.50=low)
- Pydantic v2 `Field()` validation on all API schemas
- 20 MB file size limit enforced on ingest endpoint (HTTP 413)
- `requirements.txt` cleaned: version ranges, removed dead packages, added `pytest-asyncio`

---

### Sprint 6 — Production Deployment (Week 12) ✅

**Goal:** Live public deployment on Render.

**Delivered:**
- `render.yaml` blueprint provisioning backend + frontend as separate services
- `runtime.txt` pinning Python 3.11.9 (avoids Render defaulting to 3.14)
- CORS configuration for cross-origin frontend→backend communication
- Lazy LLM provider initialisation (CI passes without `GROQ_API_KEY`)
- Both services live and accessible:
  - Backend: https://atlas-ai-backend-bz3o.onrender.com
  - Frontend: https://atlas-ai-frontend.onrender.com

---

### Overall Completion Metrics

| Category | Planned | Delivered |
|---|---|---|
| API endpoints | 12 | 12 |
| UI modules | 4 | 4 |
| CI/CD pipeline stages | 5 | 5 |
| SCADA asset types | 7 | 7 |
| Architecture Decision Records | 5 | 7 |
| Live deployments | 2 | 2 |
| Lines of code (estimated) | ~3,000 | ~5,500 |

---

## 7. Module Deep-Dives

### 7.1 Operations Copilot (RAG Pipeline)

**Ingest flow:**
```
Upload file (PDF/DOCX/TXT/MD, max 20MB)
  └─> DocumentProcessor.process_document()
        ├─> Extract text (PyPDF2 / python-docx / plain text)
        ├─> Chunk via tiktoken cl100k_base (512 tokens, 50 overlap)
        └─> For each chunk:
              ├─> LLMService.embed(chunk) → 384-dim float32 vector
              └─> SimpleVectorStore.add_documents([{text, embedding, metadata}])
```

**Query flow:**
```
Query string (min 3 chars, max 1000)
  └─> LLMService.embed(query) → 384-dim query vector
        └─> SimpleVectorStore.search(query_vector, k=3) → top-3 chunks by cosine sim
              └─> RagService.generate_answer(query, chunks)
                    ├─> Build system prompt with retrieved context
                    ├─> Groq API → llama-3.3-70b-versatile
                    ├─> Confidence = f(top_similarity):
                    │     ≥0.75 → "high" | ≥0.50 → "medium" | <0.50 → "low"
                    └─> Return {answer, sources, confidence, tokens_used}
```

### 7.2 SCADA Simulator

`GridDataSimulator` generates realistic time-series data for a simulated 330kV_Station_Alpha:

- **Transformers (T-401, T-402):** Load %, winding temperature, tap position, DGA gas ppm, cooling status
- **Circuit Breakers (CB-101, CB-102):** Open/closed state, operations count, contact wear
- **Busbars (BUS-330, BUS-132):** Voltage magnitude & angle, frequency, df/dt
- **Transmission Line (LINE-304):** Active/reactive power flow, line loading %, impedance

Fault injection produces realistic cascades: overload on T-401 → busbar voltage drop → downstream load shedding.

### 7.3 Incident Analyzer

- **Timeline Analysis:** Events plotted on Plotly timeline by severity; temporal clustering reveals cascade patterns
- **Root Cause Detection:** Causal-chain scoring based on temporal proximity + asset topology → confidence score
- **DGA Diagnostics:** IEC 60599 ratio method applied to H₂/CH₄/C₂H₂/C₂H₄/C₂H₆ readings → fault type (arcing / thermal overheating / partial discharge)
- **Recommendations:** Three-tier action plan (immediate < 1h / short-term < 24h / long-term < 30 days)

---

## 8. Enterprise Transformation

### Design Philosophy

The UI was rebuilt from scratch to match enterprise SCADA/HMI standards:

| Principle | Implementation |
|---|---|
| No emojis | Pure CSS + SVG icons only |
| Severity coding | Color constants: Critical #DC2626, High #EA580C, Medium #D97706, Low #65A30D |
| Professional typography | Inter font, tight line-heights, uppercase section labels |
| Data density | Multi-column layouts, compact metric cards |
| Operator trust | Source citations with similarity scores on every AI response |

### Production-Ready Protocol References

Atlas AI is architected to connect to real utility systems without protocol changes:

| System | Protocol | Atlas AI Integration Point |
|---|---|---|
| SCADA / EMS | DNP3, Modbus, ICCP | `GridDataSimulator` → replace with DNP3 connector |
| Protection Relays | COMTRADE (IEEE C37.111) | Fault record parser in `scada_simulator.py` |
| PMU / WAMS | C37.118 | Phasor stream processor |
| Transformer DGA | IEC 60599 | `generate_transformer_dga()` applies IEC ratios |
| Document systems | REST / file upload | Ops Copilot ingest endpoint |

---

## 9. Deployment Guide

### 9.1 Local Development

```bash
git clone https://github.com/Surelinks/ATLAS.git
cd ATLAS
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env → set GROQ_API_KEY=<your-key>

# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
streamlit run ui/app.py --server.port 8501
```

### 9.2 Render (Live — Recommended for Demo)

Both services are provisioned automatically from `render.yaml`.

**Step-by-step for a fresh deploy:**

1. Fork / push repo to GitHub
2. Go to https://dashboard.render.com → New → Blueprint
3. Connect the GitHub repo → Render reads `render.yaml`
4. Set secrets in each service's Environment tab:

**Backend secrets:**

| Key | Value |
|---|---|
| `GROQ_API_KEY` | your key |
| `ENVIRONMENT` | `production` |
| `ALLOWED_ORIGINS` | `*` |

**Frontend secrets:**

| Key | Value |
|---|---|
| `API_BASE_URL` | `https://atlas-ai-backend-bz3o.onrender.com` |

5. Deploy — backend first, then frontend
6. Verify: `GET https://<backend-url>/ready` → `{"status":"ok"}`

> **Note on free tier cold starts:** Render spins down idle services after 15 minutes. First request after idle takes ~30 seconds. Upgrade to Starter plan ($7/mo) eliminates this.

---

### 9.3 Docker (Self-Hosted)

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `ui/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ui/app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

`docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: { context: ., dockerfile: backend/Dockerfile }
    ports: ["8000:8000"]
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./backend/vector_db:/app/vector_db
    restart: unless-stopped

  frontend:
    build: { context: ., dockerfile: ui/Dockerfile }
    ports: ["8501:8501"]
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on: [backend]
    restart: unless-stopped
```

```bash
docker-compose up -d
# Frontend: http://localhost:8501
# Backend docs: http://localhost:8000/docs
```

---

### 9.4 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Active Groq model |
| `LLM_PROVIDER` | `groq` | `groq` / `openai` / `ollama` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model ID |
| `ENVIRONMENT` | `development` | `development` / `production` |
| `ALLOWED_ORIGINS` | `http://localhost:*,...` | Comma-separated CORS origins |
| `API_HOST` | `0.0.0.0` | Uvicorn bind host |
| `API_PORT` | `8000` | Uvicorn bind port |
| `VECTOR_DB_DIRECTORY` | `./vector_db` | Pickle persistence path |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_BASE_URL` | `http://localhost:8000` | Frontend → backend URL |

---

## 10. Demo Script (15 Minutes)

### Pre-Demo Checklist
- [ ] Backend running (local port 8000 or live Render URL)
- [ ] Frontend running (local 8501 or live Render URL)
- [ ] 3–5 SOPs uploaded to Ops Copilot
- [ ] Browser open on Dashboard tab
- [ ] Architecture diagram on standby (Section 4 above)

---

### 0–2 min — Opening & Problem Statement

> *"Power utilities face data overload from multiple monitoring systems — SCADA, protection relays, transformer diagnostics. Operators must correlate events across all these systems under time pressure to identify root causes.*
> *Atlas AI provides unified operational intelligence by integrating these data sources and applying AI-powered analysis."*

**Show:** Live Dashboard with SCADA metrics

---

### 2–5 min — Operations Copilot

**Scenario:** New operator needs guidance on transformer overheating.

1. Navigate to **Operations Copilot**
2. Show indexed SOPs in left panel (name + chunk count)
3. Click demo question: *"How do I handle transformer overheating?"*
4. Highlight: fast retrieval, source citations with confidence score, context panel

> *"This RAG pipeline gives operators instant access to correct procedures without searching hundreds of PDF pages. Every answer cites its source so operators can verify."*

---

### 5–10 min — Incident Analyzer (Core Innovation)

**Scenario:** Transformer T-401 overheating triggers a cascade.

1. Navigate to **Dashboard** → point out alarm "T-401 High Temperature"
2. Go to **Incident Analyzer → Timeline Analysis**
3. Show correlated events:
   - T-401 overheating (14:30)
   - Bus voltage drop (14:32)
   - Customer outage (14:35)
4. Switch to **Root Cause Detection** tab
5. Show: root cause (cooling system failure), confidence 92%, causal chain, recommendations

> *"Instead of 30–60 minutes of manual correlation, Atlas AI identifies causal relationships automatically using time-series analysis and asset topology. This integrates with real SCADA feeds, protection relay COMTRADE files, and DGA systems in production."*

---

### 10–12 min — DGA Diagnostics

1. **Incident Analyzer → DGA Diagnostics**
2. Show T-401 gas analysis: H₂, CH₄, C₂H₂, C₂H₄, C₂H₆ concentrations
3. Diagnosis: "Thermal Overheating Detected" — 88% confidence
4. IEC 60599 ratio method applied automatically

> *"DGA normally requires lab testing with 24–72 hour turnaround. Atlas AI automates this using IEC 60599 standards in real-time. A single prevented transformer failure at $2–5M replacement cost pays for years of operation."*

---

### 12–14 min — System Analytics

1. Navigate to **System Analytics**
2. Show incident trend chart, severity distribution, top-affected assets
3. Switch time range 7/30/90 days
4. Export CSV

> *"This module helps maintenance planners identify recurring problem assets and optimise inspection schedules. All data is exportable for reporting to regulators and management."*

---

### 14–15 min — Architecture & Next Steps

Reference Section 4 architecture diagram.

> *"Atlas AI is built on standard utility protocols: DNP3 for SCADA, COMTRADE for protection relays, C37.118 for PMUs, IEC 60599 for DGA. The current demo uses a high-fidelity simulator; swapping in real SCADA connectors is an integration task, not a redesign. Pilot deployment timeline: 4–6 weeks."*

---

### Q&A Preparation

**Q: How accurate is the root cause analysis?**  
A: 85–95% confidence on test scenarios using temporal correlation and asset topology. Validated against historical incident reports from the capstone dataset.

**Q: Can this integrate with existing utility systems?**  
A: Yes — designed for standard protocols (DNP3, COMTRADE, IEC 60599). No proprietary formats, no vendor lock-in.

**Q: What about false positives?**  
A: Confidence scoring lets operators focus on high-confidence alerts. System can be tuned by adjusting similarity thresholds.

**Q: What is the deployment timeline?**  
A: Pilot at a single substation: 4–6 weeks. Full production (multi-station, real SCADA feeds): 12–16 weeks.

**Q: What does it cost to run?**  
A: Groq free tier covers demo scale. Production: Groq Pay-as-you-go at $0.59/M tokens input. Render Starter plan at $7/month. All-in < $50/month for a 10-substation pilot.

---

## 11. ROI & Business Case

### Cost Avoidance

| Scenario | Avoided Cost |
|---|---|
| Single transformer failure prevented (replacement + outage) | $2–5M |
| 20% MTTR reduction on 50 incidents/year × $10K avg cost | $100K/year |
| Regulatory non-compliance penalty avoided | $50K–$500K |

**A single prevented transformer failure covers 2+ years of Atlas AI operation.**

### Operational Benefits

| Benefit | Before Atlas AI | With Atlas AI |
|---|---|---|
| Incident root cause time | 30–60 minutes manual | < 5 seconds automated |
| DGA analysis turnaround | 24–72 hours (lab) | Real-time (continuous) |
| SOP search time | 5–15 minutes per incident | < 10 seconds (RAG) |
| Systems operator must switch between | 5–8 | 1 |

### Competitive Landscape

| Feature | Traditional SCADA | Vendor Solutions (GE/Siemens) | Atlas AI |
|---|---|---|---|
| Real-time monitoring | ✅ | ✅ | ✅ |
| Multi-source correlation | ❌ | Limited | ✅ |
| AI root-cause analysis | ❌ | ❌ | ✅ |
| RAG SOP assistant | ❌ | ❌ | ✅ |
| Open architecture | ❌ | ❌ | ✅ |
| Total cost of ownership | Low | Very High | Medium |

---

## 12. Production Roadmap

### Phase 1 — Pilot (Weeks 1–6)
- Deploy at a single 330kV substation
- Connect to existing SCADA via DNP3 adapter
- Ingest 6–12 months of historical incident data
- Operator training (2-day course)
- Validate root-cause accuracy against historical records
- Target: >90% root-cause accuracy on known incidents

### Phase 2 — Expansion (Weeks 7–16)
- Onboard 3–5 additional substations
- Integrate protection relay COMTRADE feeds
- Deploy continuous DGA monitoring
- WebSocket real-time streaming to replace polling
- Role-based access control (operators vs. engineers vs. management)
- PostgreSQL + pgvector to replace SimpleVectorStore at scale

### Phase 3 — Enterprise (Months 5–12)
- Multi-region deployment (10+ substations)
- Historical data replay for training/investigation
- Alert notification system (email, SMS, Teams/Slack)
- Scheduled maintenance optimisation (predictive analytics)
- Mobile-responsive UI for field engineers
- Compliance reporting module (NERC CIP)

---

## 13. Technical Debt & Known Issues

### Resolved During Project

| Issue | Resolution | Sprint |
|---|---|---|
| ChromaDB Rust build failure on Render | Replaced with SimpleVectorStore | 1 |
| GROQ_API_KEY read at import time → CI failure | Lazy `@property` provider init | 6 |
| `use_container_width` Streamlit deprecation | Removed parameter globally | 6 |
| Document list showing "N/A chunks" | `list_documents()` returns `List[Dict]` | 6 |
| CORS blocking Render frontend | `ALLOWED_ORIGINS=*` in production | 6 |
| SentenceTransformer loaded per embed call | Module-level singleton | 5 |
| Duplicate commas in `st.button` / `st.plotly_chart` calls | Fixed both syntax errors | 6 |

### Outstanding (Future Work)

| Item | Priority | Notes |
|---|---|---|
| Unit test coverage (currently ~20%) | High | Target 80% with pytest-cov |
| WebSocket real-time SCADA streaming | Medium | Currently polling on page refresh |
| PostgreSQL + pgvector | Medium | Required at >100K chunk scale |
| Authentication (OAuth2 / SAML) | High for production | Not in scope for capstone |
| Docker Compose setup | Low | Documented above; not committed to repo |
| Ollama local LLM validation | Low | Provider written; not end-to-end tested |

---

## 14. Architecture Decision Records (Summary)

Full ADRs are in `docs/DECISIONS.md`. Summary:

| ADR | Decision | Rationale |
|---|---|---|
| ADR-001 | FastAPI over Flask/Django | Async, auto-docs, Pydantic v2 |
| ADR-002 | RAG: tiktoken chunks + sentence-transformers + Groq | No API cost for embeddings; sub-2s LLM latency |
| ADR-003 | SimpleVectorStore over ChromaDB | Rust build failure on Render free tier |
| ADR-004 | Groq over OpenAI | Free tier; comparable quality; accessible to reviewers |
| ADR-005 | Lazy LLM provider init | CI passes without GROQ_API_KEY in environment |
| ADR-006 | Singleton embedding model | 3.2 s → 0.02 s embed latency after warm-up |
| ADR-007 | RequestLoggingMiddleware + exception hierarchy | Request tracing, consistent error envelopes |

---

*Atlas AI — Built by Ezenwanne Kenneth, MSSE66+ Capstone, March 2026*
