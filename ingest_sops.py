"""
Script to bulk ingest SOP documents into Atlas AI via API
"""
import httpx
import asyncio
from pathlib import Path


async def ingest_sops():
    """Ingest all SOP documents from data/sops directory"""
    base_url = "http://localhost:8000/api/v1/ops-copilot"
    sops_dir = Path(__file__).parent / "data" / "sops"
    
    if not sops_dir.exists():
        print(f"Error: SOPs directory not found: {sops_dir}")
        return
    
    print("=" * 60)
    print("Atlas AI - SOP Ingestion Script")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Get current stats
        response = await client.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\nCurrent state:")
            print(f"   Documents: {stats.get('total_documents', 0)}")
            print(f"   Chunks: {stats.get('total_chunks', 0)}")
        
        # Ingest each SOP file
        print(f"\nIngesting SOPs from: {sops_dir}")
        print("-" * 60)
        
        files = list(sops_dir.glob("*"))
        sop_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
        
        if not sop_files:
            print("No SOP files found!")
            return
        
        success_count = 0
        for file_path in sop_files:
            print(f"\nProcessing: {file_path.name}...")
            
            try:
                with open(file_path, 'rb') as f:
                    files = {
                        'file': (file_path.name, f, 'application/octet-stream')
                    }
                    
                    response = await client.post(
                        f"{base_url}/ingest",
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   Status: Success")
                        print(f"   Chunks: {result.get('chunk_count', 0)}")
                        print(f"   Tokens: {result.get('total_tokens', 0)}")
                        success_count += 1
                    else:
                        print(f"   Status: Failed - {response.text}")
            
            except Exception as e:
                print(f"   Error: {e}")
        
        # Final stats
        print("\n" + "=" * 60)
        response = await client.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Final state:")
            print(f"   Documents: {stats.get('total_documents', 0)}")
            print(f"   Chunks: {stats.get('total_chunks', 0)}")
        
        print(f"\nIngestion complete: {success_count}/{len(sop_files)} files processed")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(ingest_sops())
