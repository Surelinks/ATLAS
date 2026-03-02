"""
Demo script for Atlas AI Ops Copilot
Ingests SOPs, runs queries, and shows statistics
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.rag.rag_service import rag_service


async def main():
    """Run complete Ops Copilot demo"""
    print("=" * 70)
    print("Atlas AI - Ops Copilot Demo")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # ====================
    # STEP 1: INGEST SOPs
    # ====================
    print("\n[STEP 1] Ingesting SOP Documents")
    print("-" * 70)
    
    sops_dir = Path(__file__).parent / "data" / "sops"
    
    if not sops_dir.exists():
        print(f"ERROR: SOP directory not found: {sops_dir}")
        return
    
    results = await rag_service.ingest_directory(sops_dir)
    
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\nIngestion Results: {success_count}/{len(results)} successful")
    print()
    
    for result in results:
        if result["status"] == "success":
            print(f"  ✓ {result['filename']:<45} {result['chunk_count']:>2} chunks  {result['total_tokens']:>5} tokens")
        else:
            print(f"  ✗ {result.get('filename', 'unknown'):<45} FAILED: {result['message']}")
    
    # ====================
    # STEP 2: STATISTICS
    # ====================
    print("\n" + "=" * 70)
    print("[STEP 2] Vector Store Statistics")
    print("-" * 70)
    
    stats = rag_service.get_statistics()
    print(f"\n  Total Documents: {stats['total_documents']}")
    print(f"  Total Chunks:    {stats['total_chunks']}")
    
    documents = rag_service.get_available_documents()
    print(f"\n  Document IDs:")
    for doc_id in documents:
        print(f"    • {doc_id}")
    
    # ====================
    # STEP 3: TEST QUERIES
    # ====================
    print("\n" + "=" * 70)
    print("[STEP 3] Testing Queries")
    print("=" * 70)
    
    test_questions = [
        {
            "question": "What is the power outage response procedure?",
            "description": "Power Outage SOP"
        },
        {
            "question": "What safety precautions are required for transformer maintenance?",
            "description": "Transformer Safety"
        },
        {
            "question": "How do I monitor grid stability?",
            "description": "Grid Monitoring"
        }
    ]
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{'─' * 70}")
        print(f"Query {i}/3: {test['description']}")
        print(f"{'─' * 70}")
        print(f"Q: {test['question']}")
        print()
        
        response = await rag_service.query(
            question=test['question'],
            top_k=2,
            include_sources=True
        )
        
        print(f"Confidence: {response['confidence'].upper()}")
        print(f"\nAnswer:")
        print(response['answer'])
        
        if response.get('sources'):
            print(f"\nSources ({len(response['sources'])}):")
            for src in response['sources']:
                print(f"  [{src['index']}] {src['document']}")
                print(f"      Similarity: {src['similarity']:.3f}")
                print(f"      \"{src['excerpt'][:80]}...\"")
    
    # ====================
    # SUMMARY
    # ====================
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print(f"\n✓ Ingested {stats['total_documents']} documents with {stats['total_chunks']} chunks")
    print(f"✓ Executed {len(test_questions)} test queries successfully")
    print(f"\nNext Steps:")
    print(f"  • Start API: cd backend && uvicorn app.main:app --reload")
    print(f"  • View docs: http://localhost:8000/docs")
    print(f"  • Run UI: streamlit run ui/streamlit_app.py")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
