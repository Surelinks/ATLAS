"""
Document Processing Service
Handles PDF/DOCX ingestion, text extraction, chunking, and embedding
"""
from typing import List, Dict, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
import hashlib

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    metadata: Dict
    token_count: int


class DocumentProcessor:
    """
    Process documents for RAG pipeline:
    1. Extract text from PDF/DOCX
    2. Chunk into overlapping segments
    3. Generate embeddings
    4. Store in vector database
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.get_encoding(encoding_name)
        logger.info(
            f"DocumentProcessor initialized: chunk_size={chunk_size}, "
            f"overlap={chunk_overlap}"
        )
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(str(file_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            logger.info(f"Extracted {len(text)} characters from {file_path.name}")
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(str(file_path))
            text = "\n\n".join([para.text for para in doc.paragraphs if para.text])
            logger.info(f"Extracted {len(text)} characters from {file_path.name}")
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise
    
    def extract_text(self, file_path: Path) -> str:
        """Extract text based on file extension"""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            return self.extract_text_from_docx(file_path)
        elif suffix in [".txt", ".md"]:
            return file_path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def chunk_text(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict] = None
    ) -> List[DocumentChunk]:
        """
        Chunk text into overlapping segments based on token count
        
        Args:
            text: Full document text
            document_id: Unique identifier for the document
            metadata: Additional metadata to attach to chunks
        
        Returns:
            List of DocumentChunk objects
        """
        if metadata is None:
            metadata = {}
        
        # Encode full text into tokens
        tokens = self.encoder.encode(text)
        chunks = []
        
        # Create overlapping chunks
        start_idx = 0
        chunk_index = 0
        
        while start_idx < len(tokens):
            # Get chunk tokens
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode back to text
            chunk_text = self.encoder.decode(chunk_tokens)
            
            # Create chunk ID (hash of content for deduplication)
            chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
            chunk_id = f"{document_id}_chunk_{chunk_index}_{chunk_hash}"
            
            # Create chunk object
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                text=chunk_text,
                chunk_index=chunk_index,
                metadata={
                    **metadata,
                    "start_token": start_idx,
                    "end_token": end_idx,
                    "total_tokens": len(tokens)
                },
                token_count=len(chunk_tokens)
            )
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.chunk_overlap
            chunk_index += 1
        
        logger.info(
            f"Created {len(chunks)} chunks from document {document_id} "
            f"({len(tokens)} total tokens)"
        )
        
        return chunks
    
    def process_document(
        self,
        file_path: Path,
        document_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> List[DocumentChunk]:
        """
        Complete document processing pipeline
        
        Args:
            file_path: Path to document file
            document_id: Optional custom ID (defaults to filename)
            metadata: Additional metadata
        
        Returns:
            List of processed document chunks
        """
        if document_id is None:
            document_id = file_path.stem  # filename without extension
        
        if metadata is None:
            metadata = {}
        
        # Add file metadata
        metadata.update({
            "filename": file_path.name,
            "file_type": file_path.suffix,
            "file_size": file_path.stat().st_size
        })
        
        # Extract text
        text = self.extract_text(file_path)
        
        if not text:
            logger.warning(f"No text extracted from {file_path}")
            return []
        
        # Chunk text
        chunks = self.chunk_text(text, document_id, metadata)
        
        return chunks
    
    def process_directory(
        self,
        directory: Path,
        file_extensions: List[str] = [".pdf", ".docx", ".txt", ".md"]
    ) -> Dict[str, List[DocumentChunk]]:
        """
        Process all documents in a directory
        
        Args:
            directory: Path to directory
            file_extensions: List of file extensions to process
        
        Returns:
            Dictionary mapping document_id to list of chunks
        """
        results = {}
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    chunks = self.process_document(file_path)
                    results[file_path.stem] = chunks
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
        
        total_chunks = sum(len(chunks) for chunks in results.values())
        logger.info(
            f"Processed {len(results)} documents, "
            f"created {total_chunks} total chunks"
        )
        
        return results


# Initialize global instance
document_processor = DocumentProcessor()
