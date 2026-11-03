from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="Control de Gastos", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_timezone: str = Field(default="America/La_Paz", alias="APP_TIMEZONE")
    default_currency: str = Field(default="BOB", alias="DEFAULT_CURRENCY")

    database_url: str = Field(
        default="postgresql+asyncpg://gastos:gastos@db:5432/gastos",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    n8n_api_key: str = Field(default="", alias="N8N_API_KEY")

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:8080",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
