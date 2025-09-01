import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_orders_counts_endpoint():
    """Test orders counts endpoint"""
    response = client.get("/api/v1/orders/counts")
    
    # Should not return 404 or 405
    assert response.status_code not in [404, 405]
    
    # If successful, should return JSON with counts
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)

def test_orders_by_status_endpoint():
    """Test orders by status endpoint"""
    response = client.get("/api/v1/orders/by-status/pending")
    
    # Should not return 404 or 405 (method not allowed)
    assert response.status_code not in [404, 405]
    
    # If successful, should return array
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
