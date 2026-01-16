import os

from fastapi.testclient import TestClient

from app.main import app


def test_scrape_requires_qty_limit_for_qty_mode():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    client = TestClient(app)
    response = client.post(
        "/scrape",
        json={
            "url": "https://m.place.naver.com/place/1414590796",
            "mode": "QTY",
        },
    )
    assert response.status_code == 422
    assert "limit_qty is required when mode is QTY" in str(response.json())


def test_scrape_requires_date_limit_for_date_mode():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    client = TestClient(app)
    response = client.post(
        "/scrape",
        json={
            "url": "https://m.place.naver.com/place/1414590796",
            "mode": "DATE",
        },
    )
    assert response.status_code == 422
    assert "limit_date is required when mode is DATE" in str(response.json())
