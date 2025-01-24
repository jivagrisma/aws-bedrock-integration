"""
Data models for AWS Bedrock integration.

This module defines the core data models used for interacting with AWS Bedrock
and Claude models, including configuration, messages, and responses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported model providers."""
    ANTHROPIC = "anthropic"


class ModelId(str, Enum):
    """Available model IDs."""
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"


class ModelInfo(BaseModel):
    """Model capabilities and limits."""
    provider: ModelProvider
    name: str
    description: str
    max_tokens: int = Field(default=8192)
    supports_streaming: bool = Field(default=True)
    supports_functions: bool = Field(default=False)
    default_temperature: float = Field(default=0.0)


@dataclass
class Message:
    """A message in the conversation."""
    role: str
    content: str
    metadata: Optional[Dict] = None


class StreamChunk(BaseModel):
    """A chunk of streamed response."""
    type: str
    text: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_write_tokens: Optional[int] = None
    cache_read_tokens: Optional[int] = None


class Usage(BaseModel):
    """Token usage information."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: Optional[int] = None
    cache_read_tokens: Optional[int] = None


class BedrockResponse(BaseModel):
    """Complete response from Bedrock."""
    model_id: str
    content: str
    usage: Usage
    metadata: Optional[Dict] = None


# Model registry
BEDROCK_MODELS: Dict[str, ModelInfo] = {
    ModelId.CLAUDE_3_SONNET.value: ModelInfo(
        provider=ModelProvider.ANTHROPIC,
        name="Claude 3 Sonnet",
        description="Latest Claude model optimized for enterprise use",
        max_tokens=8192,
        supports_streaming=True,
        supports_functions=True,
        default_temperature=0.0
    ),
    ModelId.CLAUDE_3_HAIKU.value: ModelInfo(
        provider=ModelProvider.ANTHROPIC,
        name="Claude 3 Haiku",
        description="Fast and efficient Claude model for simpler tasks",
        max_tokens=4096,
        supports_streaming=True,
        supports_functions=True,
        default_temperature=0.0
    )
}

DEFAULT_MODEL_ID = ModelId.CLAUDE_3_SONNET.value