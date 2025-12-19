from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str
    OPENAI_MODEL_TEMP: float
    OPENAI_REASONING_MODEL_NAME: str
    OPENAI_REASONING_MODEL_TEMP: float

    # Google gen AI Configuration
    GOOGLE_GENAI_API_KEY: str
    GOOGLE_GENAI_MODEL_NAME: str
    GOOGLE_GENAI_MODEL_TEMP: float

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Create a singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
