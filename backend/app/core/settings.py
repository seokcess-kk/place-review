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


@lru_cache
def get_settings() -> SettingsSnapshot:
    settings = Settings()
    return SettingsSnapshot(app_env=settings.app_env, database_url=settings.database_url)
