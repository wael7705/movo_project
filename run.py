#!/usr/bin/env python3
"""
Run script for the Movo backend application.
This script allows running the app from the project root directory.
"""

import uvicorn
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["backend"]
    )
