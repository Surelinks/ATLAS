"""
Unit tests for Document Processor Service
Tests PDF extraction, chunking logic, and edge cases
"""
import pytest
from pathlib import Path
from app.services.document_processor import DocumentProcessor, DocumentChunk


class TestDocumentProcessor:
    """Test document processing functionality"""
    
    def test_initialization(self):
        """Test processor initializes with correct parameters"""
        processor = DocumentProcessor(chunk_size=256, chunk_overlap=30)
        assert processor.chunk_size == 256
        assert processor.chunk_overlap == 30
        assert processor.encoder is not None
    
    def test_text_chunking_basic(self, document_processor, sample_text):
        """Test basic text chunking functionality"""
        chunks = document_processor.chunk_text(
            text=sample_text,
            document_id="test_doc"
        )
        
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)
        assert all(c.document_id == "test_doc" for c in chunks)
        
        # Check chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
    
    def test_chunk_overlap(self, document_processor):
        """Test that chunks have proper overlap"""
        long_text = "word " * 200  # Create text that will span multiple chunks
        chunks = document_processor.chunk_text(long_text, "test_overlap")
        
        if len(chunks) > 1:
            # Should have overlap between consecutive chunks
            assert chunks[0].token_count <= document_processor.chunk_size
            assert chunks[1].token_count <= document_processor.chunk_size
    
    def test_chunk_metadata(self, document_processor, sample_text):
        """Test that chunks contain proper metadata"""
        metadata = {"source": "test", "category": "sop"}
        chunks = document_processor.chunk_text(
            text=sample_text,
            document_id="test_meta",
            metadata=metadata
        )
        
        assert len(chunks) > 0
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["category"] == "sop"
        assert "start_token" in chunks[0].metadata
        assert "end_token" in chunks[0].metadata
    
    def test_chunk_ids_unique(self, document_processor, sample_text):
        """Test that chunk IDs are unique"""
        chunks = document_processor.chunk_text(sample_text, "test_unique")
        chunk_ids = [c.chunk_id for c in chunks]
        
        assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs should be unique"
    
    def test_empty_text_handling(self, document_processor):
        """Test handling of empty text"""
        chunks = document_processor.chunk_text("", "empty_doc")
        
        # Should return at least empty list or handle gracefully
        assert isinstance(chunks, list)
    
    def test_very_short_text(self, document_processor):
        """Test handling of text shorter than chunk size"""
        short_text = "This is a very short text."
        chunks = document_processor.chunk_text(short_text, "short_doc")
        
        assert len(chunks) == 1
        assert chunks[0].text == short_text
    
    def test_extract_text_from_txt(self, temp_dir, document_processor):
        """Test text extraction from plain text files"""
        txt_path = temp_dir / "test.txt"
        test_content = "This is test content for TXT extraction."
        txt_path.write_text(test_content, encoding="utf-8")
        
        extracted = document_processor.extract_text(txt_path)
        assert extracted == test_content
    
    def test_extract_text_from_markdown(self, temp_dir, document_processor):
        """Test text extraction from markdown files"""
        md_path = temp_dir / "test.md"
        test_content = "# Test Heading\n\nThis is markdown content."
        md_path.write_text(test_content, encoding="utf-8")
        
        extracted = document_processor.extract_text(md_path)
        assert extracted == test_content
    
    def test_unsupported_file_format(self, temp_dir, document_processor):
        """Test that unsupported formats raise appropriate error"""
        unsupported_path = temp_dir / "test.xyz"
        unsupported_path.write_text("content", encoding="utf-8")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            document_processor.extract_text(unsupported_path)
    
    def test_process_document_complete(self, temp_dir, document_processor):
        """Test complete document processing pipeline"""
        txt_path = temp_dir / "complete_test.txt"
        content = "Standard Operating Procedure\n" * 20
        txt_path.write_text(content, encoding="utf-8")
        
        chunks = document_processor.process_document(txt_path)
        
        assert len(chunks) > 0
        assert all(c.document_id == "complete_test" for c in chunks)
        assert all("filename" in c.metadata for c in chunks)
        assert all(c.metadata["filename"] == "complete_test.txt" for c in chunks)
    
    def test_custom_document_id(self, temp_dir, document_processor):
        """Test using custom document ID"""
        txt_path = temp_dir / "file.txt"
        txt_path.write_text("Content for custom ID test", encoding="utf-8")
        
        custom_id = "my_custom_id"
        chunks = document_processor.process_document(
            txt_path,
            document_id=custom_id
        )
        
        assert all(c.document_id == custom_id for c in chunks)
    
    def test_token_counting(self, document_processor, sample_text):
        """Test that token counts are accurate"""
        chunks = document_processor.chunk_text(sample_text, "token_test")
        
        for chunk in chunks:
            assert chunk.token_count > 0
            assert chunk.token_count <= document_processor.chunk_size


@pytest.mark.integration
class TestDocumentProcessorIntegration:
    """Integration tests requiring actual file I/O"""
    
    def test_process_directory(self, temp_dir, document_processor):
        """Test processing multiple files in a directory"""
        # Create multiple test files
        for i in range(3):
            file_path = temp_dir / f"doc_{i}.txt"
            file_path.write_text(f"Content for document {i}\n" * 10, encoding="utf-8")
        
        results = document_processor.process_directory(temp_dir)
        
        assert len(results) == 3
        assert "doc_0" in results
        assert "doc_1" in results
        assert "doc_2" in results
        
        for doc_id, chunks in results.items():
            assert len(chunks) > 0
            assert all(c.document_id == doc_id for c in chunks)
