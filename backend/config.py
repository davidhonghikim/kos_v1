"""
Configuration settings for KOS v1 Knowledge Library Framework
"""

import os
import sys
from typing import List, Optional
from pydantic_settings import BaseSettings


def get_required_env(key: str) -> str:
    """Get required environment variable or exit if missing"""
    value = os.getenv(key)
    if value is None:
        print(f"ERROR: Required environment variable '{key}' is not set")
        sys.exit(1)
    return value


def get_required_env_int(key: str) -> int:
    """Get required environment variable as int or exit if missing/invalid"""
    value = get_required_env(key)
    try:
        return int(value)
    except ValueError:
        print(f"ERROR: Environment variable '{key}' must be an integer, got: {value}")
        sys.exit(1)


def get_optional_env_int(key: str) -> Optional[int]:
    """Get optional environment variable as int or None"""
    value = os.getenv(key)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        print(f"WARNING: Environment variable '{key}' must be an integer, got: {value}")
        return None


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "KOS v1 Knowledge Library Framework"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = get_required_env("KOS_HOST")
    PORT: int = get_required_env_int("KOS_API_INTERNAL_PORT")
    
    # Security
    SECRET_KEY: str = get_required_env("SECRET_KEY")
    ALGORITHM: str = get_required_env("KOS_JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = get_required_env_int("KOS_JWT_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        f"http://{os.getenv('KOS_DEFAULT_HOST')}:{os.getenv('KOS_FRONTEND_EXTERNAL_PORT')}",
        f"http://{os.getenv('KOS_DEFAULT_HOST')}:{os.getenv('KOS_API_EXTERNAL_PORT')}",
        "https://kos.local",
        "https://kos.example.com",
    ]
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Vector Database
    VECTOR_DB_URL: Optional[str] = os.getenv("VECTOR_DB_URL")
    
    # AI/LLM
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Medical/DICOM
    DICOM_STORE_PATH: Optional[str] = os.getenv("DICOM_STORE_PATH")
    PACS_HOST: Optional[str] = os.getenv("PACS_HOST")
    PACS_PORT: Optional[int] = get_optional_env_int("PACS_PORT")
    PACS_AE_TITLE: Optional[str] = os.getenv("PACS_AE_TITLE")
    
    # WebAuthN
    WEBAUTHN_RP_ID: Optional[str] = os.getenv("WEBAUTHN_RP_ID")
    WEBAUTHN_RP_NAME: Optional[str] = os.getenv("WEBAUTHN_RP_NAME")
    WEBAUTHN_RP_ORIGIN: Optional[str] = os.getenv("WEBAUTHN_RP_ORIGIN")
    
    # Logging
    LOG_LEVEL: Optional[str] = os.getenv("LOG_LEVEL")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Vault
    VAULT_PATH: Optional[str] = os.getenv("VAULT_PATH")
    
    # Transformer System
    SPARK_ENABLED: bool = os.getenv("SPARK_ENABLED", "false").lower() == "true"
    CORTEX_MODE: Optional[str] = os.getenv("CORTEX_MODE")
    
    model_config = {
        "env_file": ".env"
    }


# Global settings instance
settings = Settings()
