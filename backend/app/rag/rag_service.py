"""
Atlas AI - RAG (Retrieval-Augmented Generation) Service
=========================================================
Orchestrates the full RAG pipeline for the Operations Copilot:

1. **Ingest** – accept a document, chunk it, embed each chunk, and store in
   the vector index.
2. **Retrieve** – embed the user’s question and retrieve the top-k most
   similar SOP chunks via cosine similarity.
3. **Generate** – feed retrieved context + question to the LLM and return a
   grounded, cited answer.
4. **Confidence scoring** – label answers as ``high`` / ``medium`` / ``low``
   based on the top retrieval similarity score.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""
from typing import List, Dict, Optional
import logging
from pathlib import Path

from app.services.document_processor import document_processor, DocumentChunk
from app.services.simple_vector_store import vector_store
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    Ops Copilot RAG implementation:
    1. Retrieve relevant SOP chunks
    2. Generate contextual answers using LLM
    3. Cite sources
    """
    
    def __init__(self):
        self.system_prompt = """You are an operations assistant helping engineers follow standard operating procedures (SOPs).

Your role:
- Provide accurate, step-by-step guidance from SOPs
- Highlight safety precautions
- Cite specific SOP sections
- If information is not in the provided context, say so clearly
- Use clear, professional language

Always prioritize safety and compliance."""
    
    async def ingest_document(
        self,
        file_path: Path,
        document_id: Optional[str] = None
    ) -> Dict:
        """
        Ingest a new SOP document
        
        Args:
            file_path: Path to PDF/DOCX file
            document_id: Optional custom document ID
        
        Returns:
            Ingestion results with chunk count
        """
        logger.info(f"Ingesting document: {file_path.name}")
        
        try:
            # Process document into chunks
            chunks = document_processor.process_document(
                file_path=file_path,
                document_id=document_id
            )
            
            if not chunks:
                return {
                    "status": "error",
                    "message": "No text could be extracted from document"
                }
            
            # Add chunks to vector store
            await vector_store.add_chunks(chunks, llm_service)
            
            return {
                "status": "success",
                "document_id": chunks[0].document_id,
                "filename": file_path.name,
                "chunk_count": len(chunks),
                "total_tokens": sum(c.token_count for c in chunks)
            }
        
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def ingest_directory(self, directory: Path) -> List[Dict]:
        """Ingest all documents in a directory"""
        results = []
        
        for file_path in directory.glob("*"):
            if file_path.suffix.lower() in [".pdf", ".docx", ".txt", ".md"]:
                result = await self.ingest_document(file_path)
                results.append(result)
        
        return results
    
    async def query(
        self,
        question: str,
        top_k: int = 3,
        include_sources: bool = True
    ) -> Dict:
        """
        Answer a query using RAG
        
        Args:
            question: User question about SOPs
            top_k: Number of relevant chunks to retrieve
            include_sources: Whether to include source citations
        
        Returns:
            Answer with optional source citations
        """
        logger.info(f"Processing query: {question}")
        
        try:
            # Step 1: Retrieve relevant chunks
            search_results = await vector_store.search(
                query=question,
                llm_service=llm_service,
                top_k=top_k
            )
            
            if not search_results:
                return {
                    "answer": "I don't have information about that in the available SOPs. Please check if the relevant procedures have been uploaded.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # Step 2: Extract context
            context_chunks = [r["chunk"].text for r in search_results]
            
            # Step 3: Generate answer
            answer = await llm_service.generate_with_context(
                query=question,
                context=context_chunks,
                system_prompt=self.system_prompt
            )
            
            # Step 4: Prepare response with calibrated confidence score
            top_similarity = search_results[0]["similarity"] if search_results else 0.0
            if top_similarity >= 0.75:
                confidence = "high"
            elif top_similarity >= 0.50:
                confidence = "medium"
            else:
                confidence = "low"

            response = {
                "answer": answer,
                "confidence": confidence,
            }
            
            if include_sources:
                sources = []
                for i, result in enumerate(search_results):
                    chunk = result["chunk"]
                    source = {
                        "index": i + 1,
                        "document": chunk.metadata.get("filename", "Unknown"),
                        "document_id": chunk.metadata.get("document_id", "Unknown"),
                        "excerpt": chunk.text[:200] + "...",
                        "similarity": result["similarity"]
                    }
                    sources.append(source)
                
                response["sources"] = sources
            
            logger.info("Query processed successfully")
            return response
        
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "sources": [],
                "confidence": "error"
            }
    
    def get_available_documents(self) -> List[Dict]:
        """List all ingested documents with metadata"""
        return vector_store.list_documents()
    
    def get_statistics(self) -> Dict:
        """Get RAG system statistics"""
        return vector_store.get_stats()
    
    async def delete_document(self, document_id: str) -> Dict:
        """Delete a document from the system"""
        deleted_count = vector_store.delete_document(document_id)
        
        return {
            "status": "success" if deleted_count > 0 else "not_found",
            "document_id": document_id,
            "chunks_deleted": deleted_count
        }


# Global instance
rag_service = RAGService()
