"""
Atlas AI - Operations Copilot API
====================================
REST endpoints that expose the RAG-based SOP assistant to the frontend.

Endpoints
---------
POST /api/v1/ops-copilot/query        – Answer a question using indexed SOPs
POST /api/v1/ops-copilot/ingest       – Upload and index a new SOP document
GET  /api/v1/ops-copilot/documents    – List all indexed documents
DELETE /api/v1/ops-copilot/documents/{id} – Remove a document from the index
GET  /api/v1/ops-copilot/stats        – Vector store statistics

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.rag.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Maximum file size accepted: 20 MB
_MAX_FILE_BYTES = 20 * 1024 * 1024
_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class QueryRequest(BaseModel):
    """Payload for a RAG query against indexed SOPs."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1_000,
        description="The operational question to answer.",
        examples=["What is the transformer overheating response procedure?"],
    )
    top_k: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of SOP chunks to retrieve as context.",
    )
    include_sources: Optional[bool] = Field(
        default=True,
        description="Whether to include source citations in the response.",
    )


class SourceCitation(BaseModel):
    """A single retrieved source document excerpt."""

    index: int
    document: str
    document_id: str
    excerpt: str
    similarity: float


class QueryResponse(BaseModel):
    """Response envelope for a RAG query."""

    answer: str
    confidence: str = Field(description="high | medium | low | error")
    sources: Optional[List[SourceCitation]] = []


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Ask the Ops Copilot",
    description=(
        "Submit an operational question and receive an answer grounded in the "
        "indexed SOPs, complete with source citations."
    ),
)
async def query_sops(request: QueryRequest) -> QueryResponse:
    """Answer a question using the RAG pipeline."""
    try:
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources,
        )
        return result
    except Exception as exc:
        logger.error("Query failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/ingest",
    summary="Upload and index an SOP document",
    description=(
        "Accepts a PDF, DOCX, TXT, or MD file. "
        "The document is chunked, embedded, and stored in the vector index. "
        f"Maximum file size: {_MAX_FILE_BYTES // (1024 * 1024)} MB."
    ),
)
async def ingest_document(file: UploadFile = File(...)) -> dict:
    """Upload and ingest a Standard Operating Procedure document."""
    # ---- Validate extension ----
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file_ext}'. "
                f"Allowed: {sorted(_ALLOWED_EXTENSIONS)}"
            ),
        )

    # ---- Read content & enforce size limit ----
    content = await file.read()
    if len(content) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the {_MAX_FILE_BYTES // (1024 * 1024)} MB limit."
            ),
        )

    # ---- Write to a temp file for processing ----
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        result = await rag_service.ingest_document(
            file_path=tmp_path,
            document_id=Path(file.filename or "document").stem,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Ingestion failed for '%s': %s", file.filename, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        # Always clean up the temp file
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    if result.get("status") == "error":
        raise HTTPException(status_code=422, detail=result.get("message"))

    return result


@router.get(
    "/documents",
    summary="List indexed SOP documents",
    description="Returns all documents currently stored in the vector index.",
)
async def list_documents() -> dict:
    """Return all indexed SOP documents with metadata."""
    try:
        documents = rag_service.get_available_documents()
        return {"documents": documents, "count": len(documents)}
    except Exception as exc:
        logger.error("Failed to list documents: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete(
    "/documents/{document_id}",
    summary="Delete an indexed document",
    description="Permanently removes a document and its embeddings from the vector index.",
)
async def delete_document(document_id: str) -> dict:
    """Delete a document from the vector store by ID."""
    try:
        result = await rag_service.delete_document(document_id)
        if result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Document not found")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Delete failed for '%s': %s", document_id, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/stats",
    summary="Vector store statistics",
    description="Returns total document and chunk counts for the vector index.",
)
async def get_statistics() -> dict:
    """Return vector store usage statistics."""
    try:
        return rag_service.get_statistics()
    except Exception as exc:
        logger.error("Failed to retrieve stats: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
