"""
Vector Store Service using ChromaDB
Handles document storage, retrieval, and similarity search
"""
from typing import List, Dict, Optional
import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings

from app.core.config import settings
from app.services.document_processor import DocumentChunk
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector database interface using ChromaDB
    Stores document chunks with embeddings for similarity search
    """
    
    def __init__(self, collection_name: str = "sop_documents"):
        """Initialize ChromaDB client and collection"""
        persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.Client(
            Settings(
                persist_directory=str(persist_dir),
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Atlas AI SOP documents"}
        )
        
        logger.info(
            f"VectorStore initialized: collection='{collection_name}', "
            f"docs={self.collection.count()}"
        )
    
    async def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of DocumentChunk objects to store
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        # Generate embeddings for all chunks
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = []
        
        for chunk in chunks:
            try:
                embedding = await llm_service.embed(chunk.text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to generate embedding for chunk {chunk.chunk_id}: {e}")
                # Use zero vector as fallback
                embeddings.append([0.0] * 384)  # Default embedding dimension
        
        # Prepare data for ChromaDB
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                **chunk.metadata
            }
            for chunk in chunks
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    async def search(
        self,
        query: str,
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search for relevant document chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of search results with text, metadata, and similarity scores
        """
        # Generate query embedding
        logger.info(f"Searching for: '{query[:100]}...'")
        query_embedding = await llm_service.embed(query)
        
        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                result = {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                }
                formatted_results.append(result)
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def get_document_chunks(self, document_id: str) -> List[Dict]:
        """Get all chunks for a specific document"""
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        chunks = []
        if results and results["ids"]:
            for i in range(len(results["ids"])):
                chunk = {
                    "chunk_id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                }
                chunks.append(chunk)
        
        return sorted(chunks, key=lambda x: x["metadata"]["chunk_index"])
    
    def delete_document(self, document_id: str) -> int:
        """Delete all chunks for a document"""
        # Get chunks to delete
        chunks = self.collection.get(
            where={"document_id": document_id}
        )
        
        if not chunks or not chunks["ids"]:
            logger.warning(f"No chunks found for document {document_id}")
            return 0
        
        # Delete chunks
        self.collection.delete(ids=chunks["ids"])
        logger.info(f"Deleted {len(chunks['ids'])} chunks for document {document_id}")
        
        return len(chunks["ids"])
    
    def list_documents(self) -> List[Dict]:
        """List all documents in the store"""
        all_data = self.collection.get()
        
        # Extract unique documents
        documents = {}
        if all_data and all_data["metadatas"]:
            for metadata in all_data["metadatas"]:
                doc_id = metadata["document_id"]
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata.get("filename", "unknown"),
                        "chunk_count": 0
                    }
                documents[doc_id]["chunk_count"] += 1
        
        return list(documents.values())
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            "total_chunks": self.collection.count(),
            "documents": len(self.list_documents())
        }


# Global instance
vector_store = VectorStore()
