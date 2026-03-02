# ATLAS AI - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required for demo. Production would use JWT tokens.

---

## Health Check

### GET `/api/v1/health`
Check if API server is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-07T09:30:00Z"
}
```

---

## Operations Copilot Endpoints

### 1. Upload Document

**Endpoint:** `POST /api/v1/ops-copilot/upload`

**Description:** Upload and process SOP documents (PDF or TXT).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (file upload)

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/ops-copilot/upload \
  -F "file=@/path/to/document.pdf"
```

**Response (Success - 200):**
```json
{
  "message": "Document uploaded successfully",
  "filename": "SOP_Grid_Restoration.pdf",
  "chunks": 45,
  "indexed": true
}
```

**Response (Error - 400):**
```json
{
  "detail": "Invalid file format. Only PDF and TXT supported."
}
```

---

### 2. Query RAG System

**Endpoint:** `POST /api/v1/ops-copilot/query`

**Description:** Ask questions about uploaded documents.

**Request Body:**
```json
{
  "question": "What are the steps for grid stability restoration?",
  "top_k": 3
}
```

**Parameters:**
- `question` (string, required): User's question
- `top_k` (integer, optional, default=3): Number of context chunks to retrieve

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/ops-copilot/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I handle transformer overheating?",
    "top_k": 3
  }'
```

**Response (Success - 200):**
```json
{
  "answer": "Based on SOP-2301, transformer overheating requires immediate load reduction...",
  "sources": [
    {
      "document": "SOP_Transformer_Ops.pdf",
      "relevance": 0.92,
      "chunk": "Section 4.2: Overload Protection - When transformer temperature exceeds..."
    },
    {
      "document": "Emergency_Procedures.pdf",
      "relevance": 0.87,
      "chunk": "Emergency Response: Step 1: Verify temperature readings. Step 2: Reduce load by 25%..."
    }
  ],
  "confidence": 0.89
}
```

**Response (No Documents - 404):**
```json
{
  "detail": "No documents indexed. Please upload SOPs first."
}
```

---

### 3. List Documents

**Endpoint:** `GET /api/v1/ops-copilot/documents`

**Description:** Get list of indexed documents.

**Response (Success - 200):**
```json
{
  "documents": [
    {
      "name": "SOP_Grid_Restoration.pdf",
      "uploaded_at": "2026-02-07T09:15:00Z",
      "chunks": 45,
      "size_kb": 1204
    },
    {
      "name": "Emergency_Procedures.pdf",
      "uploaded_at": "2026-02-07T08:30:00Z",
      "chunks": 32,
      "size_kb": 856
    }
  ],
  "total": 2
}
```

---

### 4. Delete Document

**Endpoint:** `DELETE /api/v1/ops-copilot/documents/{document_name}`

**Description:** Remove document from vector store.

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/ops-copilot/documents/SOP_Grid_Restoration.pdf
```

**Response (Success - 200):**
```json
{
  "message": "Document deleted successfully",
  "filename": "SOP_Grid_Restoration.pdf"
}
```

---

## Data Models

### Query Request
```typescript
{
  question: string;      // User's question
  top_k?: number;       // Number of context chunks (default: 3)
  temperature?: number; // LLM temperature (default: 0.7)
}
```

### Query Response
```typescript
{
  answer: string;           // AI-generated answer
  sources: Source[];        // Retrieved context
  confidence: number;       // Answer confidence (0-1)
  processing_time_ms: number;
}
```

### Source
```typescript
{
  document: string;    // Source document name
  relevance: number;   // Relevance score (0-1)
  chunk: string;       // Text snippet
  page?: number;       // PDF page number
}
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request body validation failed |
| 500 | Internal Error | Server error |

---

## Rate Limits
- No rate limits for demo
- Production: 100 requests/minute per IP

---

## Example Integration (Python)

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Upload document
with open("sop.pdf", "rb") as f:
    response = requests.post(
        f"{API_BASE}/ops-copilot/upload",
        files={"file": f}
    )
    print(response.json())

# Query RAG
response = requests.post(
    f"{API_BASE}/ops-copilot/query",
    json={
        "question": "What is the outage response procedure?",
        "top_k": 3
    }
)
data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {len(data['sources'])}")
```

---

## Example Integration (JavaScript)

```javascript
const API_BASE = "http://localhost:8000/api/v1";

// Upload document
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch(`${API_BASE}/ops-copilot/upload`, {
  method: "POST",
  body: formData
})
  .then(res => res.json())
  .then(data => console.log(data));

// Query RAG
fetch(`${API_BASE}/ops-copilot/query`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: "How do I handle transformer overheating?",
    top_k: 3
  })
})
  .then(res => res.json())
  .then(data => {
    console.log("Answer:", data.answer);
    console.log("Sources:", data.sources);
  });
```

---

## WebSocket (Future Feature)

Real-time SCADA data streaming:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/scada");

ws.onmessage = (event) => {
  const scadaData = JSON.parse(event.data);
  console.log("Station:", scadaData.station_id);
  console.log("Voltage:", scadaData.measurements["BUS-330"].voltage_kv);
};
```

---

## Testing with Swagger UI

Interactive API docs available at:
```
http://localhost:8000/docs
```

Alternative ReDoc format:
```
http://localhost:8000/redoc
```
