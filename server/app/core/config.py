from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    access_token: str
    refresh_token: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    environment: str = "development"
    cors_origins: str = "http://localhost:3000"
    ollama_base_url: str
    ollama_model: str

    openai_api_key: str | None = None
    openai_model: str = "gpt-4"
    github_webhook_secret: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
