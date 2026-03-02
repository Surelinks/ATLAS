"""Simple in-memory vector store for RAG without ChromaDB dependency"""
import numpy as np
from typing import List, Dict, Any, Optional
import pickle
import os
from pathlib import Path

from app.services.document_processor import DocumentChunk


class SimpleVectorStore:
    """In-memory vector store with persistence"""
    
    def __init__(self, persist_directory: str = "./vector_db"):
        self.persist_directory = persist_directory
        self.documents: Dict[str, List[DocumentChunk]] = {}
        self.embeddings: Dict[str, List[np.ndarray]] = {}
        self._load()
    
    def _load(self):
        """Load persisted data"""
        persist_path = Path(self.persist_directory)
        if persist_path.exists():
            docs_file = persist_path / "documents.pkl"
            emb_file = persist_path / "embeddings.pkl"
            
            if docs_file.exists():
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
            
            if emb_file.exists():
                with open(emb_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
    
    def _save(self):
        """Persist data to disk"""
        persist_path = Path(self.persist_directory)
        persist_path.mkdir(parents=True, exist_ok=True)
        
        with open(persist_path / "documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
        
        with open(persist_path / "embeddings.pkl", 'wb') as f:
            pickle.dump(self.embeddings, f)
    
    async def add_chunks(self, chunks: List[DocumentChunk], llm_service) -> None:
        """Add document chunks with embeddings"""
        if not chunks:
            return
        
        document_id = chunks[0].document_id
        
        # Get embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = []
        
        for text in texts:
            emb = await llm_service.embed(text)
            embeddings.append(np.array(emb))
        
        # Store
        self.documents[document_id] = chunks
        self.embeddings[document_id] = embeddings
        self._save()
    
    async def search(
        self,
        query: str,
        llm_service,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if not self.documents:
            return []
        
        # Get query embedding
        query_emb = np.array(await llm_service.embed(query))
        
        # Calculate similarities for all chunks
        results = []
        for doc_id, chunks in self.documents.items():
            doc_embeddings = self.embeddings[doc_id]
            
            for chunk, emb in zip(chunks, doc_embeddings):
                # Cosine similarity
                similarity = np.dot(query_emb, emb) / (
                    np.linalg.norm(query_emb) * np.linalg.norm(emb)
                )
                
                results.append({
                    "chunk": chunk,
                    "similarity": float(similarity),
                    "document_id": doc_id
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def list_documents(self) -> List[Dict]:
        """List all documents with metadata"""
        docs = []
        for doc_id, chunks in self.documents.items():
            if chunks:
                docs.append({
                    "id": doc_id,
                    "name": chunks[0].metadata.get("filename", doc_id),
                    "chunk_count": len(chunks)
                })
        return docs
    
    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        return self.documents.get(document_id, [])
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its embeddings"""
        if document_id in self.documents:
            del self.documents[document_id]
            del self.embeddings[document_id]
            self._save()
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        total_chunks = sum(len(chunks) for chunks in self.documents.values())
        return {
            "total_documents": len(self.documents),
            "total_chunks": total_chunks
        }


# Global instance
vector_store = SimpleVectorStore()
