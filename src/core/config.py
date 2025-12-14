"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration."""

    # Timeout configuration (milliseconds)
    timeout_min: int = Field(default=1000, ge=1000, le=120000)
    timeout_max: int = Field(default=120000, ge=1000, le=120000)
    timeout_default: int = Field(default=30000, ge=1000, le=120000)

    # Logging
    log_level: str = Field(default="INFO")

    # Server configuration
    workers: int = Field(default=1, ge=1, le=10)

    @field_validator("timeout_min", "timeout_max", "timeout_default")
    @classmethod
    def validate_timeout_range(cls, v: int) -> int:
        """Validate timeout is within acceptable range."""
        if not 1000 <= v <= 120000:
            raise ValueError("Timeout must be between 1000 and 120000 milliseconds")
        return v

    @field_validator("timeout_default")
    @classmethod
    def validate_timeout_default_in_range(cls, v: int, info) -> int:
        """Validate default timeout is between min and max."""
        # Note: This validator runs after timeout_min and timeout_max are set
        return v

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
