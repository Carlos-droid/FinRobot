import os
import pytest
from fastapi.testclient import TestClient

# Make sure finrobot-backend is in the path or we can just import from it
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../finrobot-backend")))

from main import app

client = TestClient(app)

def test_cors_preflight_allow_methods():
    # Simulate a preflight OPTIONS request from an allowed origin
    # Currently allowed origins fallback to http://localhost:1420 among others
    headers = {
        "Origin": "http://localhost:1420",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/analyzer/run", headers=headers)
    assert response.status_code == 200

    # Assert methods
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    assert "GET" in allow_methods
    assert "OPTIONS" in allow_methods
    assert "*" not in allow_methods, "Wildcard should not be present in allow_methods"

    # Assert headers
    allow_headers = response.headers.get("access-control-allow-headers", "")
    assert "Content-Type" in allow_headers
    assert "*" not in allow_headers, "Wildcard should not be present in allow_headers"

def test_cors_preflight_deny_disallowed_method():
    headers = {
        "Origin": "http://localhost:1420",
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "Content-Type",
    }
    # FastAPI's CORSMiddleware will generally return 400 for disallowed methods in preflight
    response = client.options("/api/analyzer/run", headers=headers)
    # The preflight fails or it doesn't allow the method
    assert response.status_code == 400

def test_cors_request_allowed_origin():
    # Just a simple GET to root with allowed origin
    headers = {
        "Origin": "http://localhost:1420",
    }
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:1420"
