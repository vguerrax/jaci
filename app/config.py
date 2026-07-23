from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "Jaci"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./jaci.db"
    database_ssl_mode: str | None = None

    # Backup
    backup_enabled: bool = True
    backup_dir: str = "/var/backups/jaci"
    backup_retention_days: int = 30

    # Auth
    jwt_secret_key: str = "change-me-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    secure_cookie: bool = False
    magic_link_expire_minutes: int = 15
    magic_link_resend_seconds: int = 60
    tupa_url: str = "http://localhost:8001"
    tupa_product_id: str = ""
    tupa_service_token: str | None = None
    tupa_timeout_seconds: float = 10.0

    # Email
    smtp_mock: bool = True
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str|None = None
    smtp_password: str|None = None
    smtp_from: str = "noreply@jaci.app"
    smtp_tls: bool = True

    # Application URL
    app_url: str = "http://localhost:8000"

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_mode(cls, value: bool | str) -> bool | str:
        """Aceita nomes usuais de ambiente além de booleanos."""
        if isinstance(value, str):
            normalized = value.lower().strip()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        """Usa psycopg 3 para URLs PostgreSQL fornecidas por provedores."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @model_validator(mode="after")
    def disable_secure_cookie_in_debug(self) -> "Settings":
        """Permite autenticação em desenvolvimento servido por HTTP."""
        if self.debug:
            self.secure_cookie = False
        return self

    model_config = {
        "env_file": os.getenv("ENV_FILE", ".env"),
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
