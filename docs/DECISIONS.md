# Architecture Decision Records

## ADR-001: Tech Stack Selection

**Date:** January 26, 2026  
**Status:** Accepted  
**Decision Maker:** Tech Lead

### Context
Need to select appropriate technologies for building Atlas AI that balance:
- Rapid development (solo project, 12-week timeline)
- AI/ML capabilities (RAG, embeddings)
- Demonstration value for Capstone
- Production-ready patterns

### Decision
Selected stack:
- **Backend:** FastAPI (Python)
- **AI/ML:** OpenAI GPT-4, LangChain, ChromaDB
- **Frontend:** Streamlit
- **Database:** ChromaDB (vector) + SQLite (relational)
- **Deployment:** Docker + Railway/Render

### Rationale

**FastAPI:**
- Async support for LLM calls
- Auto-generated OpenAPI docs (good for Capstone presentation)
- Strong type hints (code quality)
- Fast development with Python

**ChromaDB:**
- Lightweight vector database
- No separate server required
- Easy local development
- Sufficient for demo scale

**Streamlit:**
- Rapid UI development
- Python-native (no context switching)
- Good enough for demo
- Can be replaced with React later (mentioned in presentation)

**OpenAI + LangChain:**
- Industry-standard RAG patterns
- Extensive documentation
- Easy testing and debugging

### Consequences

**Positive:**
- Fast iteration
- Single language (Python)
- Clear separation of concerns
- Easy to demo and explain

**Negative:**
- Streamlit limitations for complex UIs
- ChromaDB not production-scale (acceptable for Capstone)

### Alternatives Considered
- **Flask vs FastAPI:** FastAPI chosen for async and auto-docs
- **pgvector vs ChromaDB:** ChromaDB chosen for simplicity
- **React vs Streamlit:** Streamlit chosen for speed

---

## ADR-002: RAG Architecture Pattern

**Date:** January 26, 2026  
**Status:** Accepted

### Context
Need to design the RAG pipeline for SOP question-answering that is:
- Accurate and relevant
- Explainable (for Capstone grading)
- Testable

### Decision
Use a **retrieval-augmented generation pattern** with:
1. Document chunking (512 tokens, 50-token overlap)
2. OpenAI embeddings (text-embedding-3-small)
3. ChromaDB vector storage
4. Top-k similarity search (k=3)
5. GPT-4 with retrieved context

### Rationale
- **Chunking strategy:** Balances context retention and retrieval precision
- **Overlap:** Prevents information loss at chunk boundaries
- **Top-k=3:** Provides sufficient context without overwhelming LLM
- **GPT-4:** Best balance of quality and cost for demo

### Testing Strategy
- Unit test chunking logic
- Test embedding generation
- Test retrieval quality with known queries
- Measure response relevance

---

## ADR-003: Incident Correlation Algorithm

**Date:** January 26, 2026  
**Status:** Proposed  
**Decision Maker:** To be finalized with DeepSeek

### Context
Need algorithm to correlate incident logs into timelines and suggest root causes.

### Proposed Approach
1. **Temporal sorting** with out-of-order handling
2. **Dependency graph** based on asset IDs
3. **Pattern detection** for cascading failures
4. **Root cause scoring** based on temporal proximity + severity

### Open Questions
- Threshold for correlation window?
- How to handle conflicting timestamps?
- Scoring algorithm details?

**Action:** Review with DeepSeek for algorithm validation

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date:** [YYYY-MM-DD]
**Status:** [Proposed | Accepted | Deprecated | Superseded]
**Decision Maker:** [Role]

### Context
[What is the issue we're facing?]

### Decision
[What we decided to do]

### Rationale
[Why we made this decision]

### Consequences
**Positive:**
- [Benefit 1]

**Negative:**
- [Tradeoff 1]

### Alternatives Considered
- [Alternative 1]: [Why rejected]
```
