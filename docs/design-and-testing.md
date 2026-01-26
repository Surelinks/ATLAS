# Atlas AI: Design & Testing Document

**Project:** Atlas AI - Operational Intelligence & Incident Response Platform  
**Author:** MSSE66+ Capstone Student  
**Date:** January 26, 2026  
**Version:** 1.0

---

## 1. Executive Summary

Atlas AI is an AI-powered platform designed to help operations teams prevent errors through SOP enforcement (Ops Copilot) and resolve incidents faster through root cause analysis (Incident Analyzer). This document outlines the system architecture, design decisions, and comprehensive testing strategy.

### Key Features
- **Ops Copilot:** RAG-based SOP question-answering and compliance checking
- **Incident Analyzer:** Timeline reconstruction and root cause inference from logs
- **Unified Dashboard:** Metrics, alerts, and audit trail

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│       Streamlit UI                  │
│  (Q&A Interface + Dashboard)        │
└──────┬──────────────────────────────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│       FastAPI Backend               │
│  ┌────────────┐  ┌────────────┐    │
│  │ Ops Copilot│  │  Incident  │    │
│  │   Module   │  │  Analyzer  │    │
│  └────────────┘  └────────────┘    │
└──────┬────────────────┬─────────────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│  ChromaDB   │  │  SQLite     │
│  (Vectors)  │  │ (Metadata)  │
└─────────────┘  └─────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│       OpenAI API                    │
│  (Embeddings + GPT-4)               │
└─────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### 2.2.1 Ops Copilot Module
**Purpose:** Enforce SOPs through AI-powered Q&A

**Components:**
- `DocumentIngestion`: PDF/text extraction and preprocessing
- `ChunkingService`: Split documents into semantic chunks
- `EmbeddingService`: Generate vectors using OpenAI
- `VectorStore`: ChromaDB interface for storage/retrieval
- `RAGService`: Orchestrate retrieval + generation

**Data Flow:**
```
SOP Document → Extract Text → Chunk (512 tokens, 50 overlap) → 
Generate Embeddings → Store in ChromaDB → Ready for Queries
```

#### 2.2.2 Incident Analyzer Module
**Purpose:** Correlate logs and suggest root causes

**Components:**
- `LogParser`: Normalize diverse log formats
- `TimelineBuilder`: Sort and correlate events
- `PatternDetector`: Identify recurring issues
- `RootCauseInferencer`: LLM-based reasoning
- `ReportGenerator`: Create human-readable summaries

**Algorithm (High-Level):**
```python
# Pseudocode for incident correlation
def correlate_incidents(logs):
    # 1. Temporal sorting with out-of-order handling
    sorted_logs = sort_with_tolerance(logs, window_seconds=300)
    
    # 2. Build dependency graph
    graph = build_asset_graph(sorted_logs)
    
    # 3. Detect correlated chains
    chains = detect_chains(graph, max_gap_seconds=600)
    
    # 4. Score root causes
    root_causes = score_by_temporal_proximity_and_severity(chains)
    
    return root_causes
```

---

## 3. Design Decisions

See [DECISIONS.md](./DECISIONS.md) for detailed Architecture Decision Records (ADRs).

### Key Decisions Summary:
- **Tech Stack:** FastAPI + ChromaDB + Streamlit (rapid development, demo-friendly)
- **RAG Pattern:** Standard retrieval-augmented generation with chunking
- **Vector DB:** ChromaDB (lightweight, sufficient for Capstone scale)
- **LLM:** OpenAI GPT-4 (balance quality/cost)

---

## 4. Testing Strategy

### 4.1 Testing Philosophy
- **Unit Tests:** Test individual components in isolation
- **Integration Tests:** Test component interactions
- **AI Model Tests:** Validate prompt quality and response structure
- **End-to-End Tests:** Simulate user workflows

### 4.2 Test Coverage Goals
- **Backend Code:** >80% coverage
- **Critical Paths:** 100% (ingestion, RAG, incident correlation)
- **API Endpoints:** All endpoints tested

### 4.3 Test Categories

#### 4.3.1 Unit Tests

**Document Ingestion (`test_document_ingestion.py`):**
```python
def test_pdf_extraction():
    """Test PDF text extraction accuracy"""
    
def test_chunking_logic():
    """Test 512-token chunking with overlap"""
    
def test_empty_document_handling():
    """Edge case: empty input"""
```

**Embedding Service (`test_embedding_service.py`):**
```python
def test_embedding_generation():
    """Test OpenAI embedding API call"""
    
def test_batch_embedding():
    """Test multiple documents"""
    
def test_api_error_handling():
    """Handle OpenAI API failures"""
```

**Vector Store (`test_vector_store.py`):**
```python
def test_document_storage():
    """Store and retrieve documents"""
    
def test_similarity_search():
    """Query returns relevant results"""
    
def test_duplicate_handling():
    """Don't store same doc twice"""
```

#### 4.3.2 Integration Tests

**RAG Pipeline (`test_rag_integration.py`):**
```python
def test_end_to_end_rag():
    """Full pipeline: ingest → query → response"""
    # 1. Ingest test SOP
    # 2. Query: "What is the power outage protocol?"
    # 3. Verify response contains relevant info
    
def test_retrieval_quality():
    """Ensure top-k results are actually relevant"""
```

**Incident Correlation (`test_incident_correlation.py`):**
```python
def test_timeline_reconstruction():
    """Given unordered logs, create correct timeline"""
    
def test_root_cause_detection():
    """Identify root cause from correlated chain"""
```

#### 4.3.3 API Tests

**Health Endpoints (`test_health_api.py`):**
```python
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**SOP Query Endpoint (`test_sop_api.py`):**
```python
def test_query_endpoint(client):
    response = client.post("/api/ops-copilot/query", json={
        "question": "What is the transformer maintenance procedure?"
    })
    assert response.status_code == 200
    assert "procedure" in response.json()["answer"].lower()
```

#### 4.3.4 Prompt Quality Tests

**Prompt Validation (`test_prompts.py`):**
```python
def test_sop_prompt_structure():
    """Verify prompt includes context and instructions"""
    
def test_prompt_token_limits():
    """Ensure prompts don't exceed model limits"""
    
def test_response_format():
    """Validate LLM returns expected JSON structure"""
```

### 4.4 Test Data Strategy

**Sample Data:**
- 3 realistic SOPs (Power Outage, Transformer Maintenance, Grid Stability)
- 50+ incident logs with 3-4 correlated chains
- Edge cases: empty files, malformed JSON, duplicate events

**Data Location:** `data/sops/`, `data/incidents/`

### 4.5 CI/CD Testing

**GitHub Actions Workflow:**
```yaml
name: CI Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=html
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 4.6 Manual Testing Checklist

**Sprint 1 Demo Readiness:**
- [ ] Can ingest 3 SOP PDFs without errors
- [ ] Query returns relevant answers for 5 test questions
- [ ] Response time <5 seconds per query
- [ ] Streamlit UI loads and displays results
- [ ] Logs show no errors

**Sprint 2 Demo Readiness:**
- [ ] Can parse 50+ incident logs
- [ ] Timeline shows correct chronological order
- [ ] Root cause suggestion is plausible
- [ ] Report generates in <10 seconds

---

## 5. Performance Considerations

### 5.1 Expected Performance
- **Document Ingestion:** <5 seconds per PDF
- **Query Response:** <5 seconds for RAG
- **Incident Analysis:** <10 seconds for 50 logs

### 5.2 Scalability Notes
- Current design: demo-scale (10-100 documents)
- Production scaling would require:
  - Replace ChromaDB with Pinecone/Weaviate
  - Add caching layer (Redis)
  - Implement batch processing
  - Add rate limiting

---

## 6. Security & Privacy

### 6.1 Data Security
- No real operational data used (all synthetic)
- API keys stored in `.env` (not committed)
- CORS configured for known origins only

### 6.2 Academic Integrity
- All AI assistance disclosed in README
- Human developer accountable for all code
- Architecture decisions documented in ADRs

---

## 7. Deployment Strategy

### 7.1 Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 7.2 Production Deployment
- **Platform:** Railway or Render (free tier)
- **Docker:** Containerize backend
- **Environment:** Separate dev/prod configs
- **Monitoring:** Basic health checks

---

## 8. Future Enhancements

### Phase 1 (MVP - Current)
- Basic RAG for SOPs
- Simple incident correlation
- Streamlit UI

### Phase 2 (Post-Capstone)
- Replace Streamlit with React
- Add authentication (Auth0)
- Implement audit trail
- Advanced analytics dashboard

### Phase 3 (Production-Ready)
- Multi-tenant support
- Real-time monitoring
- Alerting system
- Production-grade vector DB

---

## 9. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)

---

## 10. Appendix: Test Execution Results

*(To be filled after Sprint 1)*

### Sprint 1 Test Results
- Unit Tests: X/Y passed
- Integration Tests: X/Y passed
- Coverage: X%
- Known Issues: [List]

---

**Document Status:** Living document, updated weekly during sprints

**Last Updated:** January 26, 2026
