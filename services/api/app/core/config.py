from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://voicerag:voicerag_secret@localhost:5432/voicerag_db"
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    
    # We load from .env if present
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

settings = Settings()
