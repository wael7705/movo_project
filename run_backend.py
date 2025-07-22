#!/usr/bin/env python3
"""
Runner for MOVO backend: initializes DB and runs backend (FastAPI) only.
"""
import sys
import os
import asyncio

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# --- DB Initialization ---
def init_db_sync():
    from backend.database.database import init_db
    asyncio.run(init_db())

# --- Run Backend (FastAPI) ---
def run_backend():
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    print("🔄 Initializing database (if needed)...")
    try:
        init_db_sync()
        print("✅ Database initialized.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

    print("🚀 Starting backend (FastAPI) ...")
    run_backend() 