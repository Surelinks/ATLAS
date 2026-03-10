# Architecture Decision Records

> **Author:** Ezenwanne Kenneth  Atlas AI Capstone Project  
> Last updated: March 2026

---

## ADR-001: Backend Framework Selection

**Date:** January 26, 2026  
**Status:** Accepted  
**Decision Maker:** Ezenwanne Kenneth

### Context

Needed a Python web framework to expose the RAG pipeline and SCADA simulator as a REST API for the Streamlit frontend, satisfying:

- Async-first for non-blocking LLM calls
- Auto-generated OpenAPI docs (essential for Capstone review)
- Strong type-safety through Pydantic
- Minimal boilerplate

### Decision

**FastAPI** with Pydantic v2 settings, Uvicorn ASGI server, and a custom `RequestLoggingMiddleware` for request-ID tracing.

### Rationale

- Native async/await eliminates thread-pool pressure during Groq API calls
- OpenAPI docs at /docs and /redoc serve as living API documentation for the Capstone presentation
- Pydantic v2 brings significant validation-performance improvements over v1

### Alternatives Considered

| Framework | Reason Rejected |
|---|---|
| Flask | Synchronous by default; no native request validation |
| Django REST Framework | Too heavyweight; ORM overhead not needed |
| Litestar | Less ecosystem adoption; harder for reviewers to evaluate |

### Consequences

- All configuration lives in `backend/app/core/config.py` via pydantic-settings
- All errors return a consistent JSON envelope: `{"error": ..., "detail": ..., "code": ..., "request_id": ...}`

---

## ADR-002: RAG Pipeline Architecture

**Date:** January 26, 2026 | Updated: March 2026  
**Status:** Accepted

### Context

Need a retrieval-augmented generation pipeline that is accurate, explainable, and testable, without paid embedding APIs.

### Decision

| Component | Choice |
|---|---|
| Document chunking | tiktoken cl100k_base, 512 tokens, 50-token overlap |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (local, free) |
| Vector store | SimpleVectorStore  NumPy cosine similarity + pickle |
| LLM | Groq API, llama-3.3-70b-versatile |
| Top-k retrieval | k = 3 |
| Confidence scoring | Similarity thresholds: >= 0.75 = high, >= 0.50 = medium, < 0.50 = low |

### Rationale

**sentence-transformers (local):** Eliminates per-token API cost; all-MiniLM-L6-v2 delivers strong retrieval quality in a 22 MB model. The model is loaded once per process via `_get_embedding_model()` singleton to avoid multi-second cold starts on every query.

**SimpleVectorStore:** ChromaDB was rejected after its Rust-compiled dependencies caused build failures on Render's free-tier Linux image (see ADR-003). A pure-NumPy cosine similarity store is sufficient for the demonstration scale (< 10,000 chunks).

**Groq:** Sub-2-second LLM latency on free tier makes the UI feel responsive. llama-3.3-70b-versatile consistently outperforms GPT-3.5-turbo on instruction-following tasks for technical documents.

### Confidence Scoring (updated March 2026)

Previous implementation used chunk count as a proxy for confidence  unreliable because every query returns the requested k chunks. Replaced with cosine-similarity threshold scoring:

```python
top_similarity = search_results[0]["similarity"]
if top_similarity >= 0.75:
    confidence = "high"
elif top_similarity >= 0.50:
    confidence = "medium"
else:
    confidence = "low"
```

---

## ADR-003: SimpleVectorStore over ChromaDB

**Date:** March 2, 2026  
**Status:** Accepted

### Context

Initial design specified ChromaDB as the vector store. During deployment to Render's free tier, `chromadb` installation failed at the Rust compilation step for `hnswlib`. Render free instances have a 512 MB RAM build limit.

### Decision

Replace ChromaDB with a custom `SimpleVectorStore`:

- In-memory storage (dict of chunk metadata + NumPy embedding matrix)
- Cosine similarity via numpy.dot / numpy.linalg.norm
- Pickle persistence to ./vector_db/ directory
- Full CRUD: add_documents, search, list_documents, delete_document

### Consequences

**Positive:**
- Zero additional dependencies (NumPy already required by sentence-transformers)
- Deterministic behaviour, easier to unit test
- No compilation step  works on any Python 3.11 image

**Negative:**
- Not suitable for > 1M chunks (all vectors held in RAM)
- No approximate nearest-neighbour indexing (HNSW)  linear scan at query time

**Migration path:** Swap SimpleVectorStore for Qdrant (cloud) or Milvus Lite if corpus grows beyond ~100K chunks. The VectorStore abstract interface in `services/vector_store.py` isolates the change to a single file.

---

## ADR-004: Groq over OpenAI

**Date:** March 2, 2026  
**Status:** Accepted

### Context

Initial design used OpenAI GPT-4. Two constraints emerged:

1. OpenAI API costs money from the first token on a new account (GPT-4 rates)
2. Capstone reviewers should be able to reproduce the demo without a paid OpenAI subscription

### Decision

Use **Groq API** with `llama-3.3-70b-versatile` as the default provider.

| Factor | Groq | OpenAI |
|---|---|---|
| Free tier | Yes (rate-limited) | No |
| Latency | ~1.5 s | ~3-5 s (GPT-4o) |
| Context window | 128k tokens | 128k tokens |
| Instruction following | Strong | Strong |
| Cost per 1M output tokens | $0.00 (free tier) | ~$15 (GPT-4o) |

The `LLMService` provider abstraction allows switching to OpenAI or Ollama via the `LLM_PROVIDER` environment variable with no code changes.

---

## ADR-005: Lazy LLM Provider Initialisation

**Date:** March 3, 2026  
**Status:** Accepted

### Context

The CI/CD pipeline began failing at the **import** step because `LLMService.__init__` was instantiating the Groq provider, which read `settings.GROQ_API_KEY` at class construction time. In the CI environment, `GROQ_API_KEY` is not set.

### Decision

Convert `LLMService._provider` to a `@property` that initialises the provider on first access:

```python
@property
def provider(self) -> BaseLLMProvider:
    if self._provider is None:
        self._provider = self._create_provider()
    return self._provider
```

### Consequences

- CI passes without GROQ_API_KEY being set
- First request bears a negligible one-time initialisation cost (~5 ms)
- Easy to unit-test by injecting a mock provider

---

## ADR-006: Singleton Embedding Model

**Date:** March 10, 2026  
**Status:** Accepted

### Context

`GroqProvider.embed()` was instantiating `SentenceTransformer("all-MiniLM-L6-v2")` on every call. Loading the model takes ~3 seconds and downloads ~22 MB on first run, making every document ingestion request noticeably slow.

### Decision

Introduce a module-level singleton in `llm_service.py`:

```python
_embedding_model: SentenceTransformer | None = None

def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model
```

### Consequences

- Embedding latency drops from ~3.2 s to ~0.02 s after warm-up
- ~22 MB of model weights live in RAM for the process lifetime (acceptable on Render 512 MB instances)

---

## ADR-007: Middleware and Exception Handling

**Date:** March 10, 2026  
**Status:** Accepted

### Context

Production logs were hard to correlate across services because requests had no stable identifier. Additionally, different parts of the code raised bare Python exceptions that resulted in inconsistent 500 responses with stack traces leaking to clients.

### Decision

1. **RequestLoggingMiddleware** (core/middleware.py): injects a UUID X-Request-ID header on every request, logs method/path/status/duration, and echoes the ID in the response.

2. **Centralised exception hierarchy** (core/exceptions.py):

| Exception | HTTP Status | Machine Code |
|---|---|---|
| DocumentProcessingError | 422 | DOCUMENT_PROCESSING_ERROR |
| LLMProviderError | 503 | LLM_PROVIDER_ERROR |
| VectorStoreError | 500 | VECTOR_STORE_ERROR |
| DocumentNotFoundError | 404 | DOCUMENT_NOT_FOUND |

All handlers produce the same envelope:

```json
{
  "error": "Human-readable message",
  "detail": "Technical detail",
  "code": "MACHINE_CODE",
  "request_id": "uuid"
}
```

### Consequences

- No raw stack traces reach the client in production
- Every log line carries the same X-Request-ID, enabling end-to-end tracing in Render log streams
- New services can raise typed exceptions without touching main.py
