from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str
    database_url: str

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)


class SettingsSnapshot(BaseModel):
    app_env: str
    database_url: str


def convert_database_url(url: str) -> str:
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://")
    return url


@lru_cache
def get_settings() -> SettingsSnapshot:
    settings = Settings()
    db_url = convert_database_url(settings.database_url)
    return SettingsSnapshot(app_env=settings.app_env, database_url=db_url)
