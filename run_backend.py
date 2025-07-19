#!/usr/bin/env python3
"""
Unified runner for MOVO system: initializes DB, runs backend (FastAPI), and frontend (Streamlit) together.
"""
import sys
import os
import threading
import subprocess
import asyncio
import time

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# --- Check required packages ---
REQUIRED_PACKAGES = [
    'uvicorn', 'streamlit', 'folium', 'streamlit_folium', 'geopy', 'sqlalchemy', 'asyncpg', 'pydantic', 'fastapi'
]
missing = []
for pkg in REQUIRED_PACKAGES:
    try:
        __import__(pkg if pkg != 'streamlit_folium' else 'streamlit_folium')
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"❌ Missing required packages: {', '.join(missing)}")
    print("Please install them with:")
    print(f"pip install {' '.join(missing)}")
    sys.exit(1)

# --- DB Initialization ---
def init_db_sync():
    from backend.database.database import init_db
    asyncio.run(init_db())

# --- Run Streamlit Frontend ---
def run_streamlit():
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'mvp1.py'])

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

    print("🚀 Starting backend (FastAPI) and frontend (Streamlit)...")
    # Run Streamlit in a separate thread
    threading.Thread(target=run_streamlit, daemon=True).start()
    # Give Streamlit a moment to start
    time.sleep(2)
    # Run backend (blocking)
    run_backend() 

import subprocess
import time

# 1. تشغيل الباكند (FastAPI)
backend_proc = subprocess.Popen(["uvicorn", "backend.app:app", "--reload"])
time.sleep(2)  # انتظر قليلاً حتى يبدأ الباكند

# 2. تشغيل واجهة التسجيل (Streamlit)
streamlit_signup = subprocess.Popen(["streamlit", "run", "mvp1.py"])
time.sleep(1)

# 3. تشغيل واجهة تسجيل الدخول (Streamlit)
streamlit_login = subprocess.Popen(["streamlit", "run", "login.py"])

print("✅ النظام يعمل! افتح http://localhost:8000/docs للـ API و http://localhost:8501 للتسجيل و http://localhost:8502 لتسجيل الدخول.")

# 4. (اختياري) إضافة بيانات وهمية عبر سكريبت أو SQL
# subprocess.run(["psql", "-U", "postgres", "-d", "movo_db", "-f", "fake_data.sql"])

backend_proc.wait() 