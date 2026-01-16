import os

from fastapi.testclient import TestClient

from app.main import app


def test_create_job_missing_dependencies():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    client = TestClient(app)
    response = client.post(
        "/jobs",
        json={"url": "https://m.place.naver.com/place/1414590796"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "RQ/Redis dependencies are missing; install rq and redis"
