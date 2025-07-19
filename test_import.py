#!/usr/bin/env python3
"""
Test import script for MOVO backend
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing imports...")
    
    # Test config import
    from backend.config import settings
    print("✅ Config imported successfully")
    print(f"   App name: {settings.app_name}")
    print(f"   Version: {settings.version}")
    
    # Test database import
    from backend.database.database import init_db
    print("✅ Database module imported successfully")
    
    # Test models import
    from backend.models import orders, customers, restaurants, captains
    print("✅ Models imported successfully")
    
    # Test services import
    from backend.services import DeliveryService, OrderLifecycleService
    print("✅ Services imported successfully")
    
    # Test API import
    from backend.api.routes import orders as api_orders
    print("✅ API routes imported successfully")
    
    print("\n🎉 All imports successful! The backend is ready to run.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Python path: {sys.path}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1) 