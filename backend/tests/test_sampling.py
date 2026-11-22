# Owner: Issue 3 - Sampling Distributions
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mean_endpoint_exists() -> None:
    response = client.post("/sampling/mean", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_variance_endpoint_exists() -> None:
    response = client.post("/sampling/variance", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_proportion_endpoint_exists() -> None:
    response = client.post("/sampling/proportion", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
