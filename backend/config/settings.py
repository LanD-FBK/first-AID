from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    DB_ENGINE: str = "sqlite+pysqlite:///:memory:?cache=shared"

settings = Settings()
