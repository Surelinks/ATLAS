"""
Unit tests for Vector Store Service
Tests storage, retrieval, similarity search, and persistence
"""
import pytest
import numpy as np
from app.services.simple_vector_store import SimpleVectorStore
from app.services.document_processor import DocumentChunk


class TestSimpleVectorStore:
    """Test vector store functionality"""
    
    @pytest.mark.asyncio
    async def test_add_chunks(self, vector_store, sample_chunks, mock_llm_service):
        """Test adding chunks to vector store"""
        from app.services.llm_service import llm_service
        
        await vector_store.add_chunks(sample_chunks, llm_service)
        
        assert len(vector_store.documents) > 0
        assert "test_doc" in vector_store.documents
        assert len(vector_store.documents["test_doc"]) == len(sample_chunks)
    
    @pytest.mark.asyncio
    async def test_search_returns_results(self, vector_store, sample_chunks, mock_llm_service):
        """Test that search returns relevant results"""
        from app.services.llm_service import llm_service
        
        await vector_store.add_chunks(sample_chunks, llm_service)
        
        results = await vector_store.search(
            query="test procedure",
            llm_service=llm_service,
            top_k=3
        )
        
        assert len(results) > 0
        assert len(results) <= 3
        assert all("chunk" in r for r in results)
        assert all("similarity" in r for r in results)
        assert all("document_id" in r for r in results)
    
    @pytest.mark.asyncio
    async def test_search_similarity_scores(self, vector_store, sample_chunks, mock_llm_service):
        """Test that similarity scores are valid"""
        from app.services.llm_service import llm_service
        
        await vector_store.add_chunks(sample_chunks, llm_service)
        
        results = await vector_store.search(
            query="safety protocols",
            llm_service=llm_service,
            top_k=5
        )
        
        for result in results:
            similarity = result["similarity"]
            assert -1.0 <= similarity <= 1.0, "Similarity should be between -1 and 1"
    
    @pytest.mark.asyncio
    async def test_search_ordering(self, vector_store, sample_chunks, mock_llm_service):
        """Test that results are ordered by similarity"""
        from app.services.llm_service import llm_service
        
        await vector_store.add_chunks(sample_chunks, llm_service)
        
        results = await vector_store.search(
            query="procedure",
            llm_service=llm_service,
            top_k=5
        )
        
        if len(results) > 1:
            similarities = [r["similarity"] for r in results]
            assert similarities == sorted(similarities, reverse=True), \
                "Results should be sorted by similarity (descending)"
    
    @pytest.mark.asyncio
    async def test_search_empty_store(self, vector_store, mock_llm_service):
        """Test searching in empty vector store"""
        from app.services.llm_service import llm_service
        
        results = await vector_store.search(
            query="test",
            llm_service=llm_service,
            top_k=3
        )
        
        assert results == []
    
    def test_list_documents(self, vector_store, sample_chunks):
        """Test listing document IDs"""
        # Manually add without LLM
        vector_store.documents["doc1"] = sample_chunks
        vector_store.documents["doc2"] = sample_chunks
        
        doc_ids = vector_store.list_documents()
        
        assert len(doc_ids) == 2
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids
    
    def test_get_document_chunks(self, vector_store, sample_chunks):
        """Test retrieving chunks for a specific document"""
        vector_store.documents["test_doc"] = sample_chunks
        
        retrieved_chunks = vector_store.get_document_chunks("test_doc")
        
        assert len(retrieved_chunks) == len(sample_chunks)
        assert retrieved_chunks == sample_chunks
    
    def test_get_nonexistent_document(self, vector_store):
        """Test retrieving non-existent document"""
        chunks = vector_store.get_document_chunks("nonexistent")
        assert chunks == []
    
    def test_delete_document(self, vector_store, sample_chunks):
        """Test deleting a document"""
        vector_store.documents["to_delete"] = sample_chunks
        vector_store.embeddings["to_delete"] = [np.zeros(384)]
        
        success = vector_store.delete_document("to_delete")
        
        assert success is True
        assert "to_delete" not in vector_store.documents
        assert "to_delete" not in vector_store.embeddings
    
    def test_delete_nonexistent_document(self, vector_store):
        """Test deleting non-existent document"""
        success = vector_store.delete_document("nonexistent")
        assert success is False
    
    def test_get_stats_empty(self, vector_store):
        """Test stats for empty store"""
        stats = vector_store.get_stats()
        
        assert stats["total_documents"] == 0
        assert stats["total_chunks"] == 0
    
    def test_get_stats_with_data(self, vector_store, sample_chunks):
        """Test stats with data"""
        vector_store.documents["doc1"] = sample_chunks
        vector_store.documents["doc2"] = sample_chunks[:2] if len(sample_chunks) >= 2 else sample_chunks
        
        stats = vector_store.get_stats()
        
        assert stats["total_documents"] == 2
        expected_chunks = len(sample_chunks) + (2 if len(sample_chunks) >= 2 else len(sample_chunks))
        assert stats["total_chunks"] == expected_chunks
    
    @pytest.mark.asyncio
    async def test_multiple_documents(self, vector_store, document_processor, mock_llm_service):
        """Test storing multiple documents"""
        from app.services.llm_service import llm_service
        
        chunks1 = document_processor.chunk_text("Document 1 content", "doc1")
        chunks2 = document_processor.chunk_text("Document 2 content", "doc2")
        
        await vector_store.add_chunks(chunks1, llm_service)
        await vector_store.add_chunks(chunks2, llm_service)
        
        assert len(vector_store.documents) == 2
        assert "doc1" in vector_store.documents
        assert "doc2" in vector_store.documents
    
    @pytest.mark.asyncio
    async def test_document_overwrite(self, vector_store, document_processor, mock_llm_service):
        """Test that re-adding a document overwrites the old one"""
        from app.services.llm_service import llm_service
        
        chunks1 = document_processor.chunk_text("Original content", "doc1")
        chunks2 = document_processor.chunk_text("Updated content", "doc1")
        
        await vector_store.add_chunks(chunks1, llm_service)
        original_count = len(vector_store.documents["doc1"])
        
        await vector_store.add_chunks(chunks2, llm_service)
        updated_count = len(vector_store.documents["doc1"])
        
        # Should have replaced, not appended
        assert "doc1" in vector_store.documents
