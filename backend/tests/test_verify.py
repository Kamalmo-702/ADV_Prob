# Owner: Issue 5 - Check the Slides
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_slides_endpoint_exists() -> None:
    response = client.get("/verify/slides")
    assert response.status_code == 200
    body = response.json()
    assert "steps" in body and "result" in body
