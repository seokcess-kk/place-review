import os

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == "test"
