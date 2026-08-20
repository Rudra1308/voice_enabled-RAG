from pydantic_settings import BaseSettings, SettingsConfigDict


from pydantic import model_validator

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://voicerag:voicerag_secret@localhost:5432/voicerag_db"
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    
    # We load from .env if present
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    @model_validator(mode='after')
    def fix_database_url(self) -> 'Settings':
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        return self

settings = Settings()
