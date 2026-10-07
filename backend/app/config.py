from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LET THEM SPEAK BEFORE THEY BREAK"
    environment: str = "development"
    database_url: str = "sqlite:///./data/let_them_speak.db"
    cors_origins: str = "http://localhost:5173"

    ai_provider: str = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:4b"

    openai_compatible_base_url: str = "https://api.openai.com/v1"
    openai_compatible_api_key: str = ""
    openai_compatible_model: str = ""

    emergency_number: str = "112"
    mental_health_helpline: str = "14416"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
