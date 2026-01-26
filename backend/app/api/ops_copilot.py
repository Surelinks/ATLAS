"""
Ops Copilot API endpoints
RAG-based SOP question answering
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import tempfile
import logging

from app.rag.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    """SOP query request"""
    question: str
    top_k: Optional[int] = 3
    include_sources: Optional[bool] = True


class QueryResponse(BaseModel):
    """SOP query response"""
    answer: str
    confidence: str
    sources: Optional[List[dict]] = []


@router.post("/query", response_model=QueryResponse)
async def query_sops(request: QueryRequest):
    """
    Query SOPs using RAG
    
    Example:
    ```json
    {
        "question": "What is the transformer maintenance procedure?",
        "top_k": 3,
        "include_sources": true
    }
    ```
    """
    try:
        result = await rag_service.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload and ingest a new SOP document
    
    Accepts: PDF, DOCX, TXT, MD files
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".txt", ".md"]
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Ingest document
        result = await rag_service.ingest_document(
            file_path=tmp_path,
            document_id=Path(file.filename).stem
        )
        
        # Clean up temp file
        tmp_path.unlink()
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    """List all ingested SOP documents"""
    try:
        documents = rag_service.get_available_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    try:
        result = await rag_service.delete_document(document_id)
        
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Document not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get Ops Copilot statistics"""
    try:
        stats = rag_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
