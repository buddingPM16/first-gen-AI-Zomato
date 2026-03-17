import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """
    Test the server health endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_recommendation_success():
    """
    Test a valid request to the recommendation endpoint.
    Note: Since this hits the real LLM and database, we use a simple request.
    Ideally, in a full prod suite, the generate_recommendation function would be mocked.
    """
    request_payload = {
        "place": "Indiranagar",
        "cuisine": "cafe",
        "max_price": 5000,
        "min_rating": 4.0,
        "top_n": 3
    }
    
    response = client.post("/api/v1/recommend", json=request_payload)
    
    assert response.status_code == 200
    json_resp = response.json()
    assert "recommendation" in json_resp
    assert isinstance(json_resp["recommendation"], str)
    assert len(json_resp["recommendation"]) > 50

def test_recommendation_validation_error():
    """
    Test FastAPI validation: max_price cannot be negative, rating cannot exceed 5.
    """
    bad_payload = {
        "place": "Indiranagar",
        "cuisine": "cafe",
        "max_price": -100,  # Invalid
        "min_rating": 6.0,  # Invalid
        "top_n": 5
    }
    
    response = client.post("/api/v1/recommend", json=bad_payload)
    
    # Validation error expected
    assert response.status_code == 422
