from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./crm.db"
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM Provider (groq, openai, anthropic)
    LLM_PROVIDER: str = "groq"

    # API Keys
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # Model Selection (auto or specific)
    MODEL_INTENT: str = ""  # Empty = auto-select
    MODEL_EXTRACT: str = ""  # Empty = auto-select
    MODEL_ORCHESTRATE: str = ""  # Empty = auto-select

    # Fallback Models
    MODEL_INTENT_FALLBACK: str = "llama3-groq-8b-8192-tool-use-preview"
    MODEL_EXTRACT_FALLBACK: str = "mixtral-8x7b-32768"
    MODEL_ORCHESTRATE_FALLBACK: str = "llama3-groq-70b-8192-tool-use-preview"

    # LangSmith
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "hcp-agent"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
