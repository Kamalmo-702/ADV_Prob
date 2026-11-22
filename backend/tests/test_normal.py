# Owner: Issue 2 - Normal Distribution
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_probability_endpoint_exists() -> None:
    response = client.post("/normal/probability", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_inverse_endpoint_exists() -> None:
    response = client.post("/normal/inverse", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
