import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "AI Job Application Copilot API"
    api_v1_prefix: str = "/api/v1"
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
