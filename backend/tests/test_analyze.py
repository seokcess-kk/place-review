import os

from fastapi.testclient import TestClient

from app.main import app


def test_analyze_requires_api_key():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    os.environ.pop("OPENAI_API_KEY", None)
    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={"review": "친절하고 맛있어요"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "OPENAI_API_KEY is required"
