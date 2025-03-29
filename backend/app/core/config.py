from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_ISSUER_URL: str
    SUPABASE_AUDIENCE: str = "authenticated"

    # Example: OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    try:
        instance = Settings()
        return instance
    except ValueError as e:
        raise SystemExit(
            f"Fatal Error: Could not load settings from .env or environment variables: {e}"
        )


settings: Settings = get_settings()
