# Atlas AI: Design & Testing Document

**Project:** Atlas AI - Operational Intelligence & Incident Response Platform
**Author:** Ezenwanne Kenneth
**Institution:** MSSE66+ Capstone Project
**Date:** March 2026
**Version:** 2.0 (updated to reflect production implementation)
**Repository:** https://github.com/Surelinks/ATLAS
**Agile Task Board:** https://github.com/users/Surelinks/projects/2

---

## 1. Executive Summary

Atlas AI is an enterprise-grade AI platform for 330kV/132kV power substation operations. It unifies SCADA telemetry, transformer DGA diagnostics, protection relay events, and SOP documentation into a single operator-facing application, applying AI to surface the right procedure at the right moment and correlate incidents to their root cause automatically.

**Core value proposition:** Reduce Mean Time To Repair (MTTR) by 20-30% by replacing manual cross-system correlation with AI-driven root-cause analysis, and eliminate SOP search time through a retrieval-augmented generation (RAG) assistant grounded in the operator team's own procedures.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
+----------------------------------------------------------+
|                   Streamlit Frontend                      |
|  Dashboard | Ops Copilot | Incident Analyzer | Analytics  |
+------------------------+---------------------------------+
                         | HTTPS / REST
+------------------------v---------------------------------+
|               FastAPI Backend (Python 3.11)              |
|  +----------------------------------------------------+  |
|  | RequestLoggingMiddleware (X-Request-ID + timing)   |  |
|  +----------------------------------------------------+  |
|  +-----------------+  +-----------------------------+  |  |
|  |  Ops Copilot    |  |  Health / Readiness Probes  |  |  |
|  |  /api/v1/       |  |  /health  /ready            |  |  |
|  +--------+--------+  +-----------------------------+  |  |
|           |                                             |  |
|  +--------v----------------------------------------+   |  |
|  |              RAG Pipeline                        |   |  |
|  |  DocumentProcessor -> SimpleVectorStore -> LLM   |   |  |
|  |  tiktoken (512tok/50ovlp)  NumPy cosine  Groq    |   |  |
|  +-------------------------------------------------+   |  |
|  +----------------------------------------------------+  |
|  |        SCADA Simulator (GridDataSimulator)         |  |
|  |  T-401|T-402|CB-101|CB-102|BUS-330|BUS-132|LINE-304| |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
```

### 2.2 Folder Structure

```
Atlas/
+-- backend/
|   +-- app/
|       +-- api/
|       |   +-- health.py              # /health  /ready probes
|       |   +-- ops_copilot.py         # /api/v1/ops-copilot/*
|       +-- core/
|       |   +-- config.py              # pydantic-settings (all env vars)
|       |   +-- exceptions.py          # typed exception hierarchy
|       |   +-- middleware.py          # request logging + X-Request-ID
|       +-- rag/
|       |   +-- rag_service.py         # Retrieve -> Generate -> Cite
|       +-- services/
|       |   +-- document_processor.py  # PDF/DOCX extraction + chunking
|       |   +-- llm_service.py         # Groq/OpenAI/Ollama abstraction
|       |   +-- simple_vector_store.py # NumPy cosine similarity + pickle
|       |   +-- scada_simulator.py     # GridDataSimulator
|       +-- main.py                    # app factory, middleware, routers
+-- ui/app.py                          # Streamlit multi-page application
+-- data/sops/                         # SOP documents for ingestion
+-- data/incidents/                    # Sample incident JSON
+-- docs/                              # All documentation
+-- .github/workflows/                 # CI/CD pipeline
+-- render.yaml                        # Render deployment blueprint
+-- runtime.txt                        # python-3.11.9 pin
```

### 2.3 Component Descriptions

#### 2.3.1 RequestLoggingMiddleware (core/middleware.py)
Injects a UUID `X-Request-ID` header on every incoming request, logs method/path/status/duration, and echoes the ID in the response. Enables end-to-end request tracing across all log lines.

#### 2.3.2 Exception Hierarchy (core/exceptions.py)
Five typed exceptions mapped to precise HTTP status codes:

| Exception | HTTP | Machine Code |
|---|---|---|
| DocumentProcessingError | 422 | DOCUMENT_PROCESSING_ERROR |
| LLMProviderError | 503 | LLM_PROVIDER_ERROR |
| VectorStoreError | 500 | VECTOR_STORE_ERROR |
| DocumentNotFoundError | 404 | DOCUMENT_NOT_FOUND |
| AtlasBaseError | 500 | ATLAS_ERROR |

All handlers return a consistent envelope:
```json
{"error": "...", "detail": "...", "code": "...", "request_id": "uuid"}
```

#### 2.3.3 DocumentProcessor (services/document_processor.py)
- Extracts text from PDF (PyPDF2), DOCX (python-docx), TXT, MD
- Chunks via tiktoken cl100k_base encoding: 512 tokens per chunk, 50-token overlap
- 50-token overlap prevents information loss at chunk boundaries

#### 2.3.4 SimpleVectorStore (services/simple_vector_store.py)
- In-memory store: Python dict of chunk metadata + NumPy float32 embedding matrix
- Cosine similarity: `numpy.dot(query, doc) / (norm(query) * norm(doc))`
- Pickle persistence to `./vector_db/` directory on every write
- Full CRUD: add_documents, search, list_documents, delete_document

Why not ChromaDB: Rust-compiled `hnswlib` dependency caused build failure on Render free tier (512 MB RAM build limit). NumPy was already a transitive dependency, so SimpleVectorStore adds zero new dependencies.

#### 2.3.5 LLMService (services/llm_service.py)
Provider abstraction pattern supporting three backends:
- **Groq** (default): llama-3.3-70b-versatile, ~1.5s latency, free tier
- **OpenAI**: gpt-4o-mini, configurable via LLM_PROVIDER env var
- **Ollama**: local models, no API key required

The provider is **lazily initialised** via `@property` — not at import time — so the CI pipeline can import the module without a GROQ_API_KEY being set.

The `SentenceTransformer` embedding model is a **module-level singleton** (`_get_embedding_model()`): loaded once per process, reducing embed latency from ~3.2s to ~0.02s after warm-up.

#### 2.3.6 RAGService (rag/rag_service.py)
Orchestrates the full Retrieve-Generate-Cite pipeline:
1. Embed query via `LLMService.embed()`
2. Retrieve top-3 chunks via `SimpleVectorStore.search()`
3. Build system prompt with retrieved context
4. Call Groq API ? llama-3.3-70b-versatile
5. Compute confidence from top chunk cosine similarity:
   - >= 0.75 ? "high"
   - >= 0.50 ? "medium"
   - < 0.50  ? "low"
6. Return `{answer, sources, confidence, tokens_used}`

#### 2.3.7 GridDataSimulator (services/scada_simulator.py)
Generates realistic time-series telemetry for 330kV_Station_Alpha:

| Asset | Type | Simulated Data | Protocol |
|---|---|---|---|
| T-401 | Transformer 330/132kV | Load%, temp, tap, DGA gases | DNP3, IEC 60599 |
| T-402 | Transformer 330/132kV | Load%, temp, tap, DGA gases | DNP3, IEC 60599 |
| CB-101 | Circuit Breaker 330kV | State, operations count | DNP3 |
| CB-102 | Circuit Breaker 132kV | State, contact wear | DNP3 |
| BUS-330 | 330kV Busbar | Voltage, angle, frequency | ICCP, PMU C37.118 |
| BUS-132 | 132kV Busbar | Voltage, angle, df/dt | ICCP, PMU C37.118 |
| LINE-304 | Transmission Line | Power flow, loading%, impedance | COMTRADE C37.111 |

---

## 3. Design & Architecture Decisions

All decisions are documented as full Architecture Decision Records (ADRs) in `docs/DECISIONS.md`. Summary:

### ADR-001: FastAPI over Flask/Django
**Decision:** FastAPI + Pydantic v2 + Uvicorn  
**Rationale:** Native async/await for non-blocking LLM calls; auto-generated OpenAPI docs at `/docs` and `/redoc`; Pydantic v2 validation performance. Flask is synchronous by default; Django too heavyweight with no ORM needed.

### ADR-002: RAG Pipeline Design
**Decision:** tiktoken chunking (512/50) + sentence-transformers + Groq  
**Rationale:** Local embeddings via `all-MiniLM-L6-v2` (22MB, no API cost). Groq free tier provides sub-2s LLM latency. Top-k=3 gives sufficient context without exceeding prompt budget.

### ADR-003: SimpleVectorStore over ChromaDB
**Decision:** Custom NumPy cosine similarity store  
**Rationale:** ChromaDB's Rust `hnswlib` compilation failed on Render free tier. NumPy already a transitive dependency. Sufficient for < 10,000 chunks at demo scale. Migration path: swap to Qdrant via the abstract `VectorStore` interface.

### ADR-004: Groq over OpenAI
**Decision:** Groq API with llama-3.3-70b-versatile  
**Rationale:** Free tier — no cost barrier for reviewers to reproduce the demo. ~1.5s latency vs ~3-5s for GPT-4o. Comparable instruction-following quality on technical documents.

### ADR-005: Lazy LLM Provider Initialisation
**Decision:** `@property` pattern for `LLMService._provider`  
**Rationale:** CI pipeline failed because `GROQ_API_KEY` is not set in CI environment. Lazy init defers key access to first request, not import time.

### ADR-006: Singleton Embedding Model
**Decision:** Module-level `_embedding_model` singleton via `_get_embedding_model()`  
**Rationale:** SentenceTransformer was instantiated on every `embed()` call (~3.2s). Singleton loads once per process ? ~0.02s per call after warm-up.

### ADR-007: Middleware + Exception Hierarchy
**Decision:** RequestLoggingMiddleware + 5 typed exceptions + 4 FastAPI handlers  
**Rationale:** No consistent request correlation in logs. Raw Python exceptions leaked stack traces to clients. Typed exceptions map to precise HTTP codes; UUID request IDs enable log correlation.

### Software Patterns Used

| Pattern | Where Used | Purpose |
|---|---|---|
| Repository / Service Layer | `SimpleVectorStore`, `LLMService`, `DocumentProcessor` | Separation of concerns; swap implementations without touching business logic |
| Provider Abstraction | `BaseLLMProvider` ? `GroqProvider`, `OpenAIProvider`, `OllamaProvider` | Switch LLM backend via env var, no code changes |
| Singleton | `_get_embedding_model()` | Load expensive model once per process |
| Lazy Initialisation | `LLMService.provider` property | Defer API-key access to runtime |
| Chain of Responsibility | FastAPI exception handlers in `exceptions.py` | Most-specific handler wins; generic fallback catches all |
| Middleware Pipeline | `RequestLoggingMiddleware` ? CORS ? router | Cross-cutting concerns separated from business logic |
| RAG (Retrieval-Augmented Generation) | `RagService` | Ground LLM answers in verified SOP documents |

---

## 4. Testing Strategy & Results

### 4.1 Testing Philosophy
- **Fail fast in CI** — syntax errors, import errors, and obvious regressions caught before merge
- **Integration over mocks** — test the actual RAG pipeline end-to-end against real Groq responses where possible
- **Security baseline** — bandit + safety on every push

### 4.2 CI/CD Pipeline (GitHub Actions)

Every push to `master` triggers `.github/workflows/ci.yml`:

```
Stage 1: Lint
  black --check .
  isort --check-only .
  flake8 backend/ ui/

Stage 2: Syntax validation
  python -m py_compile backend/app/main.py
  python -m py_compile ui/app.py
  (all backend modules)

Stage 3: Tests
  pytest backend/tests/ -v --cov=app --cov-report=xml

Stage 4: Security
  bandit -r backend/app/
  safety check

Stage 5: Build validation
  python -c "from app.main import app"
  (import smoke test without runtime secrets)
```

All 5 stages must pass before Render auto-deploys.

### 4.3 Unit Tests

**DocumentProcessor tests** (`backend/tests/test_document_processor.py`):

```python
def test_pdf_extraction():
    """PDF text extraction returns non-empty string"""

def test_txt_extraction():
    """Plain text passthrough preserves content"""

def test_chunking_produces_correct_sizes():
    """Chunks are <= 512 tokens with 50-token overlap"""

def test_empty_document_raises():
    """Empty input raises DocumentProcessingError"""

def test_chunk_overlap_preserves_boundary_context():
    """Adjacent chunks share the 50-token boundary"""
```

**SimpleVectorStore tests** (`backend/tests/test_vector_store.py`):

```python
def test_add_and_retrieve_documents():
    """Stored document is returned on search"""

def test_cosine_similarity_ranking():
    """More similar document ranked higher"""

def test_delete_document_removes_all_chunks():
    """All chunks for a document ID are removed"""

def test_list_documents_returns_dicts():
    """list_documents() returns List[Dict] with name and chunk_count"""

def test_persistence_survives_reload():
    """Pickle save/load round-trip preserves embeddings"""
```

**LLMService tests** (`backend/tests/test_llm_service.py`):

```python
def test_lazy_init_no_api_key_required_at_import():
    """LLMService can be imported without GROQ_API_KEY set"""

def test_embedding_model_singleton():
    """Two calls to _get_embedding_model() return same object"""

def test_provider_selection_via_env():
    """LLM_PROVIDER=openai selects OpenAIProvider"""
```

**RagService tests** (`backend/tests/test_rag_service.py`):

```python
def test_confidence_high_above_075():
    """Similarity >= 0.75 produces confidence='high'"""

def test_confidence_medium_050_to_075():
    """Similarity 0.50-0.74 produces confidence='medium'"""

def test_confidence_low_below_050():
    """Similarity < 0.50 produces confidence='low'"""

def test_no_results_returns_no_context_response():
    """Empty vector store returns graceful fallback answer"""
```

### 4.4 Integration Tests

**RAG pipeline end-to-end** (`backend/tests/test_rag_integration.py`):

```python
def test_ingest_then_query():
    """
    1. Ingest a known SOP text file
    2. Query with a question whose answer is in the SOP
    3. Assert answer contains expected keywords
    4. Assert confidence is 'medium' or 'high'
    5. Assert sources list contains the ingested filename
    """

def test_query_without_documents_returns_graceful_response():
    """Empty store returns answer explaining no context available"""
```

**API endpoint integration** (`backend/tests/test_api.py`):

```python
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ready_endpoint_with_empty_store():
    response = client.get("/ready")
    # Returns 200 even with empty store (degraded, not down)
    assert response.status_code in [200, 503]

def test_ingest_txt_file():
    files = {"file": ("test.txt", b"Transformer overheating procedure...", "text/plain")}
    response = client.post("/api/v1/ops-copilot/ingest", files=files)
    assert response.status_code == 200
    assert response.json()["chunks_created"] > 0

def test_ingest_oversized_file_returns_413():
    big_content = b"x" * (21 * 1024 * 1024)  # 21MB
    files = {"file": ("big.txt", big_content, "text/plain")}
    response = client.post("/api/v1/ops-copilot/ingest", files=files)
    assert response.status_code == 413

def test_query_short_string_returns_422():
    response = client.post("/api/v1/ops-copilot/query", json={"query": "ab"})
    assert response.status_code == 422

def test_delete_nonexistent_document_returns_404():
    response = client.delete("/api/v1/ops-copilot/documents/nonexistent-id")
    assert response.status_code == 404

def test_request_id_header_present():
    response = client.get("/health")
    assert "x-request-id" in response.headers

def test_response_time_header_present():
    response = client.get("/health")
    assert "x-response-time" in response.headers
```

### 4.5 Security Tests

**Bandit** (static analysis) — runs on every CI push:
- No hardcoded secrets
- No use of `subprocess.shell=True`
- No unsafe deserialization

**Safety** — checks all installed packages against known CVE database on every CI push.

### 4.6 Manual Testing Checklist

**Sprint 1 — Ops Copilot MVP:**
- [x] Ingest PDF SOP without errors
- [x] Ingest DOCX SOP without errors
- [x] Query returns relevant answer with source citations
- [x] Query response time < 5 seconds
- [x] Confidence score reflects similarity (high/medium/low)
- [x] Document list shows name and chunk count

**Sprint 2 — SCADA & Incident Analyzer:**
- [x] Dashboard shows live SCADA metrics for all 7 assets
- [x] T-401/T-402 DGA gas values update on refresh
- [x] Incident timeline displays correlated events in order
- [x] Root cause tab shows confidence score and causal chain
- [x] DGA diagnostics identifies fault type (arcing/overheating/discharge)

**Sprint 3 — Enterprise UI:**
- [x] No emojis visible anywhere in the UI
- [x] Severity-coded metric cards render correctly
- [x] Dark theme loads on first visit
- [x] All Plotly charts render without console errors
- [x] Streamlit branding hidden

**Sprint 4 — Analytics:**
- [x] 7/30/90-day range selector changes chart data
- [x] CSV export downloads correct data
- [x] Plotly PNG export works

**Sprint 5 — CI/CD:**
- [x] GitHub Actions all 5 stages pass on clean push
- [x] X-Request-ID present in every response header
- [x] X-Response-Time present in every response header
- [x] HTTP 413 returned for files > 20MB
- [x] HTTP 404 returned for missing document IDs
- [x] HTTP 422 returned for queries < 3 characters

**Sprint 6 — Production:**
- [x] Backend /ready returns 200 on Render
- [x] Frontend connects to backend on Render
- [x] CI passes without GROQ_API_KEY in environment
- [x] CORS allows Render frontend origin

### 4.7 Performance Benchmarks (measured locally)

| Operation | Target | Measured |
|---|---|---|
| Document ingestion (1-page TXT) | < 5s | ~0.8s |
| Document ingestion (10-page PDF) | < 10s | ~3.2s |
| Query (warm embedding model) | < 5s | ~2.1s |
| Query (cold embedding model) | < 10s | ~5.4s |
| Embedding after singleton warm-up | < 0.1s | ~0.02s |
| Health endpoint | < 100ms | ~12ms |

---

## 5. API Reference

### Base URLs
- Local: `http://localhost:8000`
- Production: `https://atlas-ai-backend-bz3o.onrender.com`

### Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | /health | Liveness probe | None |
| GET | /ready | Readiness probe (checks deps) | None |
| GET | / | Service info + author | None |
| POST | /api/v1/ops-copilot/query | Ask the RAG assistant | None |
| POST | /api/v1/ops-copilot/ingest | Upload SOP document | None |
| GET | /api/v1/ops-copilot/documents | List indexed documents | None |
| DELETE | /api/v1/ops-copilot/documents/{id} | Remove document | None |
| GET | /api/v1/ops-copilot/stats | Vector store statistics | None |

### Request / Response Examples

**POST /api/v1/ops-copilot/query**
```json
Request:  {"query": "What is the transformer overheating procedure?"}
Response: {
  "answer": "According to SOP-TR-001, when transformer winding temperature exceeds 105C...",
  "sources": [{"document": "SOP-TR-001.pdf", "chunk": 3, "similarity": 0.82}],
  "confidence": "high",
  "tokens_used": 847
}
```

**POST /api/v1/ops-copilot/ingest**
```
Request:  multipart/form-data, file field (PDF/DOCX/TXT/MD, max 20MB)
Response: {"document_id": "uuid", "filename": "SOP-TR-001.pdf", "chunks_created": 12}
```

---

## 6. Security & Configuration

### Environment Variables
All secrets and configuration are injected via environment variables, never committed to the repository.

| Variable | Scope | Notes |
|---|---|---|
| GROQ_API_KEY | Backend runtime only | Not present in CI, not in .env.example |
| ENVIRONMENT | Backend | development / production |
| ALLOWED_ORIGINS | Backend | * in production, specific origins in dev |

### Security Measures
- `.env` listed in `.gitignore` — API keys never committed
- Bandit static analysis on every CI push
- Safety CVE scan on every CI push
- No raw stack traces exposed to clients in production (exception handlers strip them)
- File upload restricted to .pdf/.docx/.txt/.md extensions and 20MB maximum
- Pydantic v2 Field() validation on all API inputs

---

## 7. Deployment Architecture

See `docs/PROJECT_REPORT.md` Section 9 for full deployment guide.

### Render Production Setup
```
GitHub push to master
  --> GitHub Actions CI (lint, test, security, build)
      --> Render auto-deploy (if CI passes)
          --> Backend: uvicorn app.main:app --host 0.0.0.0 --port $PORT
          --> Frontend: streamlit run ui/app.py --server.port $PORT
```

### Key Files
- `render.yaml` — service definitions and env var declarations
- `runtime.txt` — pins Python 3.11.9 to prevent Render defaulting to 3.14
- `.github/workflows/ci.yml` — full 5-stage CI pipeline

---

## 8. Future Enhancements

### High Priority (Production Path)
- PostgreSQL + pgvector to replace SimpleVectorStore at > 100K chunks
- WebSocket real-time SCADA streaming (currently polling on refresh)
- OAuth2 / SAML authentication and role-based access control (operators vs engineers vs management)
- Unit test coverage from ~20% to target 80%

### Medium Priority
- Multi-station support (currently single 330kV_Station_Alpha)
- Historical data replay for incident investigation training
- Alert notification system (email, SMS, Microsoft Teams)

### Low Priority
- React frontend to replace Streamlit for mobile-responsive UI
- NERC CIP compliance reporting module
- Kubernetes deployment for horizontal scaling

---

## 9. References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic v2 Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- sentence-transformers: https://www.sbert.net/
- Groq API: https://console.groq.com/docs
- IEC 60599 (DGA standard): https://webstore.iec.ch/publication/2594
- IEEE C37.118 (PMU standard): https://standards.ieee.org/ieee/C37.118.1/4493/
- COMTRADE IEEE C37.111: https://standards.ieee.org/ieee/C37.111/3795/

---

**Document Status:** Final — reflects production deployment as of March 2026
**Last Updated:** March 11, 2026
**Author:** Ezenwanne Kenneth
