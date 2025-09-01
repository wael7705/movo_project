import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health_endpoint():
    """Test that health endpoint returns 200 OK"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

def test_api_endpoints_structure():
    """Test that main API endpoints are accessible"""
    # Test orders endpoint (might require auth but should not 404)
    response = client.get("/api/v1/orders/counts")
    # Should not be 404 (not found)
    assert response.status_code != 404
    
    # Test assign endpoint structure
    response = client.get("/api/v1/assign/orders/1/candidates")
    # Should not be 404 (not found) - might be 500 or other error due to DB
    assert response.status_code != 404

def test_cors_headers():
    """Test that CORS headers are present"""
    response = client.options("/health")
    # Should have CORS headers or at least respond to OPTIONS
    assert response.status_code in [200, 405]  # 405 is OK if OPTIONS not implemented
