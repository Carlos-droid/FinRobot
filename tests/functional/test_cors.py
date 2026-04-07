import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to sys.path to allow importing finrobot-backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'finrobot-backend')))
from main import app, ALLOWED_ORIGINS

client = TestClient(app)

def test_cors_preflight_valid_origin():
    """
    Test that an OPTIONS request with a valid origin gets the correct
    CORS headers in the response.
    """
    # Assuming at least one valid origin exists
    valid_origin = ALLOWED_ORIGINS[0]

    headers = {
        "Origin": valid_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }

    response = client.options("/api/analyzer/run", headers=headers)

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == valid_origin
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "Content-Type" in response.headers.get("access-control-allow-headers", "")

def test_cors_preflight_invalid_origin():
    """
    Test that an OPTIONS request with an invalid origin does NOT get
    the CORS headers.
    """
    headers = {
        "Origin": "https://malicious-site.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }

    response = client.options("/api/analyzer/run", headers=headers)

    # FastAPI CORSMiddleware returns 400 Bad Request for invalid origins
    # or passes through if allow_credentials=True and it's not preflight.
    # We assert that the CORS headers are missing.
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers

def test_cors_get_valid_origin():
    """
    Test that a GET request with a valid origin gets the correct
    CORS headers in the response.
    """
    valid_origin = ALLOWED_ORIGINS[0]

    headers = {
        "Origin": valid_origin
    }

    response = client.get("/", headers=headers)

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == valid_origin
    # allow-methods and allow-headers are only sent on preflight requests (OPTIONS), not GET
