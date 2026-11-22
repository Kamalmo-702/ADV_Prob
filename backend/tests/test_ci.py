# Owner: Issue 4 - Confidence Intervals & Sample Size
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mean_endpoint_exists() -> None:
    response = client.post("/ci/mean", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_sample_size_endpoint_exists() -> None:
    response = client.post("/ci/sample-size", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
