from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CONTROL_", env_file=None, extra="forbid", hide_input_in_errors=True
    )

    environment: Literal["local", "test"] = "local"
    organization_registration: Literal["controlled"] = "controlled"
    database_host: str = Field(default="127.0.0.1", pattern=r"^[a-zA-Z0-9.:-]{1,253}$")
    database_port: int = Field(default=5432, ge=1, le=65535)
    database_name: str = Field(default="kryptroom", pattern=r"^[a-z][a-z0-9_]{0,62}$")
    database_user: str = Field(default="kryptroom_app", pattern=r"^[a-z][a-z0-9_]{0,62}$")
    database_password: SecretStr | None = Field(default=None, exclude=True)
    database_password_file: Path | None = Field(default=None, exclude=True)
    database_sslmode: Literal["require", "verify-full", "disable"] = "require"
    database_connect_timeout: int = Field(default=2, ge=1, le=10)
    database_statement_timeout_ms: int = Field(default=2000, ge=100, le=10000)
    database_pool_size: int = Field(default=5, ge=1, le=20)
    docs_enabled: bool = False

    @model_validator(mode="after")
    def load_password(self) -> "Settings":
        if (self.database_password is None) == (self.database_password_file is None):
            raise ValueError("Configure exactly one database password source")
        if self.database_password_file is not None:
            try:
                # Secret files are supplied by the local operator, never by an HTTP request.
                value = self.database_password_file.read_text(encoding="utf-8").rstrip("\r\n")
            except (OSError, UnicodeError):
                raise ValueError("Database credential file unavailable") from None
            self.database_password = SecretStr(value)
        password = self.database_password
        if password is None or len(password.get_secret_value()) < 24:
            raise ValueError("Database credential must contain at least 24 characters")
        return self

    def database_url(self) -> URL:
        if self.database_password is None:
            raise RuntimeError("Database credential unavailable")
        return URL.create(
            "postgresql+psycopg",
            username=self.database_user,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
            query={"sslmode": self.database_sslmode},
        )


def load_settings() -> Settings:
    try:
        return Settings()
    except ValueError:
        # Never let framework startup reporting stringify credential-bearing validation input.
        raise RuntimeError("Invalid Control API configuration; inspect local settings") from None
