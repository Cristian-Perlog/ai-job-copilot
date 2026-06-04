from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root (.env lives here): core -> app -> backend -> repo root
BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "AI Job Application Copilot API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    database_url: str
    frontend_origin: str = "http://localhost:3000"
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


settings = Settings()
