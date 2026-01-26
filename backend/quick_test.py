"""
Simple API startup test
"""
print("🧪 Testing Atlas AI Startup...")
print()

try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
    print(f"✅ App title: {app.title}")
    print(f"✅ Version: {app.version}")
    print()
    print("🎉 Atlas AI is configured and ready!")
    print()
    print("Next steps:")
    print("1. Start server: uvicorn app.main:app --reload")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test endpoint: POST /api/v1/ops-copilot/query")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
