import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Amauta Wearable AI Node"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Server
    HOST: str = os.getenv("AMAUTA_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("AMAUTA_PORT", "8000"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://amauta.local",
        "https://amauta.example.com",
    ]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./amauta.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Vault
    VAULT_PATH: str = os.getenv("VAULT_PATH", "./vault")
    VAULT_KEY_SIZE: int = 32
    VAULT_SALT_SIZE: int = 16

    # LLM
    LOCAL_LLM_PATH: str = os.getenv("LOCAL_LLM_PATH", "./models")
    REMOTE_LLM_ENDPOINT: str = os.getenv("REMOTE_LLM_ENDPOINT", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Vector Store
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
    VECTOR_DB_API_KEY: str = os.getenv("VECTOR_DB_API_KEY", "")

    # Medical
    DICOM_STORAGE_PATH: str = os.getenv("DICOM_STORAGE_PATH", "./dicom")
    PACS_HOST: str = os.getenv("PACS_HOST", "localhost")
    PACS_PORT: int = int(os.getenv("PACS_PORT", "11112"))
    PACS_AE_TITLE: str = os.getenv("PACS_AE_TITLE", "AMAUTA")

    # Health Monitoring
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    VITALS_UPDATE_INTERVAL: int = int(os.getenv("VITALS_UPDATE_INTERVAL", "5"))

    # Plugin System
    PLUGIN_PATH: str = os.getenv("PLUGIN_PATH", "./plugins")
    PLUGIN_REGISTRY_URL: str = os.getenv("PLUGIN_REGISTRY_URL", "")

    # WebAuthN
    WEBAUTHN_RP_ID: str = os.getenv("WEBAUTHN_RP_ID", "amauta.local")
    WEBAUTHN_RP_NAME: str = os.getenv("WEBAUTHN_RP_NAME", "Amauta Wearable AI")
    WEBAUTHN_RP_ORIGIN: str = os.getenv("WEBAUTHN_RP_ORIGIN", "https://amauta.local")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/amauta.log")

    # Monitoring
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
