import os

from app.core.settings import get_settings


def test_settings_reads_database_url():
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/place_review"
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.database_url.endswith("place_review")
