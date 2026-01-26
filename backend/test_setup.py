"""
Quick test script to verify Groq LLM and ingestion work
Run from backend directory: python test_setup.py
"""
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_service import llm_service
from app.rag.rag_service import rag_service


async def test_llm():
    """Test LLM generation"""
    print("🧪 Testing Groq LLM...")
    
    try:
        response = await llm_service.generate(
            prompt="Say 'Hello from Atlas AI!' in a friendly way.",
            temperature=0.7,
            max_tokens=50
        )
        print(f"✅ LLM Response: {response}\n")
        return True
    except Exception as e:
        print(f"❌ LLM Test Failed: {e}\n")
        return False


async def test_embeddings():
    """Test embedding generation"""
    print("🧪 Testing Free Embeddings...")
    
    try:
        embedding = await llm_service.embed("Test text for embedding")
        print(f"✅ Generated embedding with {len(embedding)} dimensions\n")
        return True
    except Exception as e:
        print(f"❌ Embedding Test Failed: {e}\n")
        return False


async def test_document_ingestion():
    """Test SOP document ingestion"""
    print("🧪 Testing SOP Ingestion...")
    
    sops_dir = Path("../data/sops")
    
    if not sops_dir.exists():
        print(f"❌ SOP directory not found: {sops_dir}\n")
        return False
    
    try:
        # Get list of PDF files
        pdf_files = list(sops_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found in data/sops\n")
            return False
        
        # Ingest first SOP as test
        test_file = pdf_files[0]
        print(f"   Ingesting: {test_file.name}")
        
        result = await rag_service.ingest_document(test_file)
        
        if result["status"] == "success":
            print(f"✅ Ingested {result['chunk_count']} chunks from {result['filename']}\n")
            return True
        else:
            print(f"❌ Ingestion failed: {result.get('message', 'Unknown error')}\n")
            return False
    
    except Exception as e:
        print(f"❌ Ingestion Test Failed: {e}\n")
        return False


async def test_query():
    """Test RAG query"""
    print("🧪 Testing RAG Query...")
    
    try:
        result = await rag_service.query(
            question="What safety precautions should be taken?",
            top_k=2
        )
        
        print(f"✅ Query successful!")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Answer: {result['answer'][:150]}...")
        print(f"   Sources: {len(result.get('sources', []))}\n")
        return True
    
    except Exception as e:
        print(f"❌ Query Test Failed: {e}\n")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 ATLAS AI - SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("LLM Generation", test_llm),
        ("Embeddings", test_embeddings),
        ("Document Ingestion", test_document_ingestion),
        ("RAG Query", test_query)
    ]
    
    results = []
    
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All systems operational! Atlas AI is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
