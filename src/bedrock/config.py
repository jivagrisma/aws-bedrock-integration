"""
Configuration management for AWS Bedrock integration.

This module handles configuration loading from .env file and provides
type-safe configuration objects for the Bedrock client.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

from .models import DEFAULT_MODEL_ID, BEDROCK_MODELS

# Cargar variables de entorno desde .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def load_env_bool(key: str, default: bool = False) -> bool:
    """Cargar variable de entorno booleana."""
    return os.getenv(key, str(default)).lower() == 'true'


def load_env_int(key: str, default: int) -> int:
    """Cargar variable de entorno numérica."""
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def load_env_float(key: str, default: float) -> float:
    """Cargar variable de entorno decimal."""
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


class BedrockConfig(BaseModel):
    """Configuration for AWS Bedrock client."""

    # AWS Credentials
    access_key_id: str = Field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""),
        description="AWS access key ID"
    )
    secret_access_key: str = Field(
        default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        description="AWS secret access key"
    )
    session_token: Optional[str] = Field(
        default_factory=lambda: os.getenv("AWS_SESSION_TOKEN"),
        description="AWS session token (optional)"
    )
    region: str = Field(
        default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"),
        description="AWS region"
    )

    # Model Configuration
    model_id: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID),
        description="Bedrock model ID"
    )
    temperature: float = Field(
        default_factory=lambda: load_env_float("BEDROCK_TEMPERATURE", 0.0),
        ge=0.0,
        le=1.0,
        description="Model temperature (0.0 to 1.0)"
    )
    max_tokens: int = Field(
        default_factory=lambda: load_env_int("BEDROCK_MAX_TOKENS", 8192),
        gt=0,
        description="Maximum tokens in response"
    )

    # Advanced Options
    use_cross_region: bool = Field(
        default_factory=lambda: load_env_bool("BEDROCK_USE_CROSS_REGION", False),
        description="Whether to use cross-region inference"
    )
    max_retries: int = Field(
        default_factory=lambda: load_env_int("BEDROCK_MAX_RETRIES", 3),
        ge=0,
        description="Maximum number of retry attempts"
    )
    timeout: int = Field(
        default_factory=lambda: load_env_int("BEDROCK_TIMEOUT", 30),
        gt=0,
        description="Request timeout in seconds"
    )
    cache_responses: bool = Field(
        default_factory=lambda: load_env_bool("BEDROCK_CACHE_RESPONSES", True),
        description="Whether to enable response caching"
    )

    # Request Headers
    headers: dict = Field(
        default_factory=lambda: {
            "anthropic-beta": "prompt-caching-2024-07-31",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        description="Custom headers for API requests"
    )

    @validator("model_id")
    def validate_model_id(cls, v: str) -> str:
        """Validate that the model ID exists in our registry."""
        if v not in BEDROCK_MODELS:
            raise ValueError(
                f"Invalid model ID: {v}. Must be one of: {list(BEDROCK_MODELS.keys())}"
            )
        return v

    @validator("region")
    def validate_region(cls, v: str) -> str:
        """Validate AWS region format."""
        valid_regions = [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-central-1",
            "ap-northeast-1", "ap-southeast-1", "ap-southeast-2"
        ]
        if v not in valid_regions:
            raise ValueError(
                f"Invalid AWS region: {v}. Must be one of: {valid_regions}"
            )
        return v

    def get_aws_config(self):
        """Get AWS configuration dictionary."""
        return {
            "region_name": self.region,
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "aws_session_token": self.session_token,
        }

    def get_request_config(self):
        """Get request configuration dictionary."""
        return {
            "max_attempts": self.max_retries,
            "mode": "adaptive",
            "connect_timeout": self.timeout,
            "read_timeout": self.timeout,
        }

    class Config:
        """Pydantic model configuration."""
        env_prefix = "BEDROCK_"
        case_sensitive = False
        validate_assignment = True


# Crear instancia global de configuración
config = BedrockConfig()