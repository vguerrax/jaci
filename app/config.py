from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Jaci"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./jaci.db"

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

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
