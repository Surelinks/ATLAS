# ATLAS AI - Testing Documentation

## Test Coverage Overview

This document outlines testing strategies, test cases, and validation procedures for Atlas AI.

---

## Test Environment Setup

### Prerequisites
```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Navigate to backend
cd backend
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rag.py -v

# Run tests matching pattern
pytest tests/ -k "test_upload" -v
```

---

## Unit Tests

### 1. RAG Service Tests

**File:** `backend/tests/test_rag_service.py`

```python
import pytest
from app.rag.rag_service import RAGService

@pytest.fixture
def rag_service():
    return RAGService()

def test_document_processing(rag_service):
    """Test document chunking and embedding"""
    text = "This is a test document for SOP procedures."
    chunks = rag_service.process_document(text)
    
    assert len(chunks) > 0
    assert all(len(chunk) > 0 for chunk in chunks)

def test_vector_search(rag_service):
    """Test similarity search"""
    # Add test documents
    rag_service.add_documents([
        {"text": "Grid restoration procedure", "metadata": {"doc": "sop1.pdf"}},
        {"text": "Transformer maintenance steps", "metadata": {"doc": "sop2.pdf"}}
    ])
    
    # Search
    results = rag_service.search("restoration", top_k=1)
    
    assert len(results) == 1
    assert "restoration" in results[0]["text"].lower()

def test_empty_query(rag_service):
    """Test handling of empty query"""
    with pytest.raises(ValueError):
        rag_service.search("", top_k=3)
```

**Expected Results:**
- ✅ Document processing creates valid chunks
- ✅ Vector search returns relevant results
- ✅ Edge cases handled gracefully

---

### 2. LLM Service Tests

**File:** `backend/tests/test_llm_service.py`

```python
import pytest
from app.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    return LLMService()

@pytest.mark.asyncio
async def test_generate_answer():
    """Test LLM answer generation"""
    service = LLMService()
    
    context = ["Step 1: Check voltage levels", "Step 2: Verify circuit breakers"]
    question = "What are the voltage check steps?"
    
    answer = await service.generate_answer(question, context)
    
    assert len(answer) > 0
    assert "voltage" in answer.lower()

@pytest.mark.asyncio
async def test_no_context():
    """Test LLM with no context"""
    service = LLMService()
    
    with pytest.raises(ValueError):
        await service.generate_answer("test question", [])
```

**Expected Results:**
- ✅ LLM generates coherent answers
- ✅ Context is properly utilized
- ✅ Empty context raises error

---

### 3. SCADA Simulator Tests

**File:** `backend/tests/test_scada_simulator.py`

```python
import pytest
from app.services.scada_simulator import GridDataSimulator, simulate_historical_incidents

def test_scada_data_generation():
    """Test SCADA telemetry generation"""
    sim = GridDataSimulator(station_id="TEST-STATION")
    data = sim.generate_scada_telemetry()
    
    assert data.station_id == "TEST-STATION"
    assert len(data.measurements) == 7  # 7 assets
    assert data.frequency_hz >= 59.0 and data.frequency_hz <= 61.0

def test_transformer_dga():
    """Test DGA analysis"""
    sim = GridDataSimulator()
    dga = sim.generate_transformer_dga("T-401")
    
    assert dga.asset_id == "T-401"
    assert dga.h2_ppm >= 0
    assert dga.diagnosis in ["Normal Aging", "Thermal Fault", "Electrical Arcing", "Partial Discharge"]

def test_historical_incidents():
    """Test incident simulation"""
    incidents = simulate_historical_incidents(days_back=7)
    
    assert len(incidents) > 0
    assert all("timestamp" in inc for inc in incidents)
    assert all("severity" in inc for inc in incidents)
```

**Expected Results:**
- ✅ SCADA data within realistic ranges
- ✅ DGA diagnosis follows IEC 60599 standard
- ✅ Historical incidents span requested time range

---

## Integration Tests

### 1. API Endpoint Tests

**File:** `backend/tests/test_api.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_upload_document():
    """Test document upload"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        response = await client.post("/api/v1/ops-copilot/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

@pytest.mark.asyncio
async def test_query_without_documents():
    """Test query with no indexed documents"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/ops-copilot/query",
            json={"question": "test", "top_k": 3}
        )
        
        assert response.status_code == 404  # No documents

@pytest.mark.asyncio
async def test_invalid_upload():
    """Test upload with invalid file type"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("test.exe", b"Invalid", "application/x-msdownload")}
        response = await client.post("/api/v1/ops-copilot/upload", files=files)
        
        assert response.status_code == 400
```

**Expected Results:**
- ✅ All endpoints return correct status codes
- ✅ Valid requests processed successfully
- ✅ Invalid requests rejected with appropriate errors

---

## End-to-End Tests

### RAG Pipeline Test

**Scenario:** User uploads SOP and asks question

```python
@pytest.mark.asyncio
async def test_full_rag_pipeline():
    """Test complete RAG workflow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Upload document
        sop_content = """
        Grid Restoration Procedure:
        Step 1: Verify all circuit breakers are open
        Step 2: Check voltage levels on all buses
        Step 3: Energize main transformer
        """
        
        files = {"file": ("sop.txt", sop_content.encode(), "text/plain")}
        upload_response = await client.post("/api/v1/ops-copilot/upload", files=files)
        assert upload_response.status_code == 200
        
        # 2. Query
        query_response = await client.post(
            "/api/v1/ops-copilot/query",
            json={
                "question": "What are the steps for grid restoration?",
                "top_k": 3
            }
        )
        
        assert query_response.status_code == 200
        data = query_response.json()
        
        # 3. Validate response
        assert "answer" in data
        assert "sources" in data
        assert "Step 1" in data["answer"] or "circuit breakers" in data["answer"].lower()
        assert len(data["sources"]) > 0
```

**Expected Results:**
- ✅ Document uploaded and indexed
- ✅ Query returns relevant answer
- ✅ Sources correctly cited

---

## Frontend Tests (Manual)

### 1. Dashboard Module

**Test Case:** SCADA Metrics Display

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Dashboard | Page loads without errors |
| 2 | Check metric cards | 4 cards visible with values |
| 3 | Verify status colors | Green for normal, red for critical |
| 4 | Check asset telemetry tabs | Transformers/CBs/Busbars tabs work |
| 5 | View incident log | Recent alarms displayed |

**Pass Criteria:** All metrics display realistic values, colors match severity.

---

### 2. Operations Copilot

**Test Case:** Document Upload and Query

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click "Operations Copilot" | Module loads |
| 2 | Upload test PDF | "Document indexed" message |
| 3 | Check document list | Uploaded file appears |
| 4 | Ask demo question | Answer appears in chat |
| 5 | Verify sources | Context panel shows relevant docs |
| 6 | Export chat history | CSV downloads |

**Pass Criteria:** Full RAG pipeline works end-to-end.

---

### 3. Incident Analyzer

**Test Case:** Search, Filter, and Pagination

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to Incident Analyzer | Timeline chart loads |
| 2 | Enter search query | Results filtered |
| 3 | Select severity filter | Only matching incidents shown |
| 4 | Navigate pagination | Next/Prev buttons work |
| 5 | Click export button | CSV downloads |
| 6 | Check Root Cause tab | Analysis displays |
| 7 | View DGA Diagnostics | Gas concentrations shown |

**Pass Criteria:** All filters work, pagination correct, exports successful.

---

### 4. System Analytics

**Test Case:** Charts and Export

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open System Analytics | Page loads |
| 2 | Change time range | Charts update |
| 3 | Zoom on trend chart | Zoom works |
| 4 | Download chart as PNG | Image downloads |
| 5 | Click export analytics | CSV downloads |

**Pass Criteria:** Interactive charts work, exports successful.

---

### 5. Theme Toggle

**Test Case:** Dark/Light Theme Switch

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open sidebar | Settings section visible |
| 2 | Click "Light" button | UI changes to light theme |
| 3 | Check text contrast | All text readable |
| 4 | Click "Dark" button | Returns to dark theme |
| 5 | Refresh page | Theme persists |

**Pass Criteria:** Both themes work, all text legible.

---

### 6. Keyboard Shortcuts

**Test Case:** Shortcut Functionality

| Shortcut | Expected Action | Pass/Fail |
|----------|----------------|-----------|
| Ctrl+K | Focus search bar | ⬜ |
| Ctrl+U | Open upload dialog | ⬜ |
| Ctrl+Enter | Send chat message | ⬜ |
| Ctrl+E | Trigger export | ⬜ |
| Esc | Clear filters | ⬜ |

**Pass Criteria:** All shortcuts perform correct actions.

---

## Performance Tests

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
```

```python
from locust import HttpUser, task, between

class AtlasUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def query_copilot(self):
        self.client.post("/api/v1/ops-copilot/query", json={
            "question": "What is the grid restoration procedure?",
            "top_k": 3
        })
    
    @task(1)
    def upload_document(self):
        files = {"file": ("test.txt", b"Test content")}
        self.client.post("/api/v1/ops-copilot/upload", files=files)
```

```bash
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

**Performance Targets:**
- ✅ API response time < 2s (95th percentile)
- ✅ Support 50 concurrent users
- ✅ Document upload < 5s for 5MB PDF
- ✅ Memory usage < 2GB under load

---

## Security Tests

### 1. Input Validation

```python
def test_sql_injection_attempt():
    """Test SQL injection protection"""
    malicious_input = "'; DROP TABLE users; --"
    response = requests.post(
        "http://localhost:8000/api/v1/ops-copilot/query",
        json={"question": malicious_input, "top_k": 3}
    )
    assert response.status_code != 500  # Should not crash

def test_xss_attempt():
    """Test XSS protection"""
    xss_payload = "<script>alert('xss')</script>"
    # Should be sanitized
```

### 2. File Upload Security

```python
def test_executable_upload_blocked():
    """Test executable files are rejected"""
    files = {"file": ("malware.exe", b"MZ", "application/x-msdownload")}
    response = requests.post(
        "http://localhost:8000/api/v1/ops-copilot/upload",
        files=files
    )
    assert response.status_code == 400

def test_oversized_file_rejected():
    """Test large file rejection"""
    large_content = b"A" * (26 * 1024 * 1024)  # 26MB
    files = {"file": ("huge.pdf", large_content, "application/pdf")}
    response = requests.post(
        "http://localhost:8000/api/v1/ops-copilot/upload",
        files=files
    )
    assert response.status_code == 413  # Payload too large
```

---

## Regression Test Suite

### Pre-Deployment Checklist

Run before each deployment:

```bash
#!/bin/bash
# test_suite.sh

echo "=== Atlas AI Test Suite ==="

# 1. Unit tests
echo "[1/5] Running unit tests..."
pytest backend/tests/ -v || exit 1

# 2. API health check
echo "[2/5] Checking API health..."
curl -f http://localhost:8000/api/v1/health || exit 1

# 3. Frontend smoke test
echo "[3/5] Checking frontend..."
curl -f http://localhost:8501 || exit 1

# 4. Document upload test
echo "[4/5] Testing document upload..."
curl -X POST http://localhost:8000/api/v1/ops-copilot/upload \
  -F "file=@test_data/sample_sop.pdf" || exit 1

# 5. Query test
echo "[5/5] Testing RAG query..."
curl -X POST http://localhost:8000/api/v1/ops-copilot/query \
  -H "Content-Type: application/json" \
  -d '{"question":"test","top_k":3}' || exit 1

echo "✅ All tests passed!"
```

---

## Bug Reporting Template

When reporting issues, include:

```markdown
**Bug Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: Windows/Linux/Mac
- Python: 3.x
- Browser: Chrome/Firefox/etc

**Logs:**
```
Paste relevant error logs
```

**Screenshots:**
[Attach if applicable]
```

---

## Test Data

Sample files for testing:

- `test_data/sample_sop.pdf` - 2-page SOP document
- `test_data/empty.txt` - Empty file (edge case)
- `test_data/large_manual.pdf` - 50-page manual (performance test)
- `test_data/invalid.exe` - Executable file (security test)

---

## Continuous Integration

### GitHub Actions Workflow

`.github/workflows/test.yml`:
```yaml
name: Atlas AI Tests

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
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Maintenance

**Weekly:**
- Review failed tests
- Update test data
- Check coverage reports

**Monthly:**
- Add tests for new features
- Refactor flaky tests
- Update performance baselines

**Quarterly:**
- Full regression suite
- Security audit
- Load testing
