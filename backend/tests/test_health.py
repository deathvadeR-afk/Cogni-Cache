import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test that the health endpoint returns a valid response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert "request_id" in data
    # Check that X-Request-ID header is present
    assert "X-Request-ID" in response.headers

def test_health_endpoint_rate_limiting():
    """Test that rate limiting is applied to the health endpoint."""
    # Make 11 requests (limit is 10 per minute)
    for _ in range(11):
        response = client.get("/api/v1/health")
    # The last request should be rate limited
    assert response.status_code == 429
    data = response.json()
    assert "error" in data
