"""
Test configuration and fixtures for Atlas AI
"""
import pytest
import sys
from pathlib import Path
from typing import Generator
import tempfile
import shutil

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_processor import DocumentProcessor
from app.services.simple_vector_store import SimpleVectorStore
from app.services.llm_service import LLMService
from app.rag.rag_service import RAGService


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_text() -> str:
    """Sample text for testing"""
    return """
    Standard Operating Procedure: Test Document
    Version: 1.0
    
    1. Purpose
    This is a test document for unit testing.
    
    2. Scope
    This document covers test scenarios.
    
    3. Procedures
    Step 1: Read the document
    Step 2: Process the text
    Step 3: Validate results
    
    4. Safety
    Always follow safety protocols.
    """


@pytest.fixture
def sample_pdf(temp_dir: Path) -> Path:
    """Create a sample PDF for testing"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = temp_dir / "test_document.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "Test SOP Document")
    c.drawString(100, 730, "This is a test procedure for unit testing.")
    c.drawString(100, 710, "Step 1: Initialize system")
    c.drawString(100, 690, "Step 2: Execute process")
    c.drawString(100, 670, "Step 3: Verify results")
    c.save()
    
    return pdf_path


@pytest.fixture
def document_processor() -> DocumentProcessor:
    """Initialize document processor"""
    return DocumentProcessor(chunk_size=128, chunk_overlap=20)


@pytest.fixture
def vector_store() -> SimpleVectorStore:
    """Initialize fresh vector store for each test"""
    store = SimpleVectorStore()
    # Clear any existing data
    store.documents = {}
    store.embeddings = {}
    return store


@pytest.fixture
def sample_chunks(document_processor: DocumentProcessor, sample_text: str):
    """Generate sample chunks for testing"""
    return document_processor.chunk_text(
        text=sample_text,
        document_id="test_doc",
        metadata={"filename": "test.txt", "source": "test"}
    )


# Mock LLM responses for testing without API calls
@pytest.fixture
def mock_llm_service(monkeypatch):
    """Mock LLM service to avoid real API calls in tests"""
    import numpy as np
    
    async def mock_generate(self, *args, **kwargs):
        return "This is a mocked LLM response for testing."
    
    async def mock_embed(self, text: str):
        # Return a consistent fake embedding vector
        np.random.seed(hash(text) % 2**32)
        return np.random.rand(384).tolist()
    
    monkeypatch.setattr(
        "app.services.llm_service.LLMService.generate",
        mock_generate
    )
    monkeypatch.setattr(
        "app.services.llm_service.LLMService.embed",
        mock_embed
    )
