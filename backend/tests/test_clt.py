# Owner: Issue 5 - CLT Simulator
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_simulate_endpoint_exists() -> None:
    response = client.post("/clt/simulate", json={})
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
