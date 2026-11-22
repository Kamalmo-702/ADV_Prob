# Owner: Issue 2 - t / Chi-square / F Explorer
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_t_distribution_endpoint_exists() -> None:
    response = client.post("/dist/t", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_chi2_distribution_endpoint_exists() -> None:
    response = client.post("/dist/chi2", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body


def test_f_distribution_endpoint_exists() -> None:
    response = client.post("/dist/f", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
