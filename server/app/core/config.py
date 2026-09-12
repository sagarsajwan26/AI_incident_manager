from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    access_token: str
    refresh_token: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    ollama_base_url: str
    ollama_model: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
