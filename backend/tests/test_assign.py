import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_assign_candidates_endpoint():
    """Test captain candidates endpoint"""
    response = client.get("/api/v1/assign/orders/1/candidates")
    
    # Should not return 404 or 405
    assert response.status_code not in [404, 405]
    
    # If successful, should return array of candidates
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        # Each candidate should have required fields
        for candidate in data:
            assert "captain_id" in candidate
            assert "captain_name" in candidate
            assert "distance_km" in candidate

def test_assign_candidates_with_params():
    """Test candidates endpoint with parameters"""
    response = client.get("/api/v1/assign/orders/1/candidates?radius_km=10&max_candidates=3")
    
    # Should not return 404 or 405
    assert response.status_code not in [404, 405]
    
    # If successful, should respect max_candidates limit
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3  # Should respect max_candidates

def test_encoding_test_endpoint():
    """Test Arabic encoding endpoint"""
    response = client.get("/api/v1/assign/test-encoding")
    
    # Should not return 404 or 405
    assert response.status_code not in [404, 405]
    
    # If successful, should return Arabic text
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
