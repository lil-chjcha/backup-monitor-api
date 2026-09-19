from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backup Monitor API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://backup:backup@db:5432/backup_monitor"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
