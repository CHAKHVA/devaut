import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")

    LOCAL_POSTGRES_SERVER: str = os.getenv("LOCAL_POSTGRES_SERVER")
    LOCAL_POSTGRES_PORT: str = os.getenv("LOCAL_POSTGRES_PORT")
    LOCAL_POSTGRES_USER: str = os.getenv("LOCAL_POSTGRES_USER")
    LOCAL_POSTGRES_PASSWORD: str = os.getenv("LOCAL_POSTGRES_PASSWORD")
    LOCAL_POSTGRES_DB: str = os.getenv("LOCAL_POSTGRES_DB")

    CLOUD_SQL_INSTANCE_CONNECTION_NAME: str = os.getenv(
        "CLOUD_SQL_INSTANCE_CONNECTION_NAME"
    )
    CLOUD_POSTGRES_SERVER: str = os.getenv("CLOUD_POSTGRES_SERVER")
    CLOUD_POSTGRES_PORT: str = os.getenv("CLOUD_POSTGRES_PORT")
    CLOUD_POSTGRES_USER: str = os.getenv("CLOUD_POSTGRES_USER")
    CLOUD_POSTGRES_PASSWORD: str = os.getenv("CLOUD_POSTGRES_PASSWORD")
    CLOUD_POSTGRES_DB: str = os.getenv("CLOUD_POSTGRES_DB")

    DATABASE_URL: PostgresDsn | None = None

    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION")

    VERTEX_AI_MODEL_NAME: str = os.getenv("VERTEX_AI_MODEL_NAME")

    API_V1_STR: str = os.getenv("API_V1_STR")

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


def build_database_url(settings: Settings) -> PostgresDsn:
    env = settings.ENVIRONMENT.lower()
    if env == "development":
        if not all(
            [
                settings.LOCAL_POSTGRES_USER,
                settings.LOCAL_POSTGRES_PASSWORD,
                settings.LOCAL_POSTGRES_SERVER,
                settings.LOCAL_POSTGRES_DB,
            ]
        ):
            raise ValueError("Missing required local database configuration variables")
        return PostgresDsn(
            f"postgresql://{settings.LOCAL_POSTGRES_USER}:{settings.LOCAL_POSTGRES_PASSWORD}@{settings.LOCAL_POSTGRES_SERVER}:{settings.LOCAL_POSTGRES_PORT}/{settings.LOCAL_POSTGRES_DB}"
        )
    else:
        if not all(
            [
                settings.CLOUD_POSTGRES_USER,
                settings.CLOUD_POSTGRES_PASSWORD,
                settings.CLOUD_POSTGRES_SERVER,
                settings.CLOUD_POSTGRES_DB,
            ]
        ):
            raise ValueError(
                "Missing required cloud database configuration variables (check CLOUD_POSTGRES_*)"
            )
        return PostgresDsn(
            f"postgresql://{settings.CLOUD_POSTGRES_USER}:{settings.CLOUD_POSTGRES_PASSWORD}@{settings.CLOUD_POSTGRES_SERVER}:{settings.CLOUD_POSTGRES_PORT}/{settings.CLOUD_POSTGRES_DB}"
        )


@lru_cache()
def get_settings() -> Settings:
    try:
        instance = Settings()

        instance.DATABASE_URL = build_database_url(instance)

        if not instance.DATABASE_URL:
            raise ValueError("DATABASE_URL could not be determined.")

        if instance.ENVIRONMENT != "development" and not instance.GCP_PROJECT_ID:
            logger.warning(
                "Warning: GCP_PROJECT_ID is not set for non-development environment."
            )

        return instance
    except ValueError as e:
        raise SystemExit(
            f"Fatal Error: Could not load settings from .env or environment variables: {e}"
        )


settings: Settings = get_settings()
