from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Receipt Keeper API"
    env: str = "local"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"
    storage_dir: str = "storage"
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.1"
    ollama_timeout_seconds: int = 120
    ocr_lang: str = "en"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
