"""
Test script to verify Atlas AI RAG pipeline
1. Ingests SOP documents
2. Tests a sample query
3. Verifies Groq API integration
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.rag.rag_service import rag_service


async def test_rag_pipeline():
    """Test complete RAG pipeline"""
    print("=" * 60)
    print("Atlas AI - RAG Pipeline Test")
    print("=" * 60)
    
    # Step 1: Ingest SOPs
    print("\n📄 Step 1: Ingesting SOP documents...")
    sops_dir = Path(__file__).parent / "data" / "sops"
    
    if not sops_dir.exists():
        print(f"❌ SOP directory not found: {sops_dir}")
        return
    
    results = await rag_service.ingest_directory(sops_dir)
    
    print(f"\n✅ Ingested {len(results)} documents:")
    for result in results:
        if result["status"] == "success":
            print(f"   • {result['filename']}: {result['chunk_count']} chunks ({result['total_tokens']} tokens)")
        else:
            print(f"   ❌ {result.get('filename', 'unknown')}: {result['message']}")
    
    # Step 2: Get stats
    print("\n📊 Vector Store Statistics:")
    stats = rag_service.get_statistics()
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Documents: {stats['total_documents']}")
    
    # Step 3: Test query
    print("\n🔍 Step 2: Testing RAG query...")
    test_questions = [
        "What is the power outage response procedure?",
        "What safety precautions are required for transformer maintenance?",
        "How do I monitor grid stability?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─' * 60}")
        print(f"Question {i}: {question}")
        print(f"{'─' * 60}")
        
        response = await rag_service.query(question, top_k=2, include_sources=True)
        
        print(f"\n💡 Answer ({response['confidence']} confidence):")
        print(response['answer'])
        
        if response.get('sources'):
            print(f"\n📚 Sources:")
            for source in response['sources']:
                print(f"   {source['index']}. {source['document']}")
                print(f"      {source['excerpt'][:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_rag_pipeline())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
