from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str

    log_level: LogLevel = "INFO"

    logfire_token: str | None = None
    logfire_service_name: str = "rag-poc"
    logfire_environment: str = "local"
    logfire_console: bool = False

    gemini_api_key: str | None = Field(default=None)
    open_router_api_key: str | None = Field(default=None)

    @property
    def database_url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_database,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.model_validate({})
