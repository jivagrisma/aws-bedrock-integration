"""
AWS Bedrock client implementation.

This module provides a robust client for interacting with AWS Bedrock,
with support for streaming, error handling, and retry logic.
"""

import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Union

import boto3
from botocore.config import Config

from .config import BedrockConfig, config as default_config
from .models import Message, StreamChunk, BedrockResponse, Usage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BedrockError(Exception):
    """Base exception for Bedrock client errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.cause = cause

    def __str__(self) -> str:
        if self.cause:
            return f"{super().__str__()} (Caused by: {str(self.cause)})"
        return super().__str__()


class BedrockClient:
    """Client for interacting with AWS Bedrock's Claude model."""

    def __init__(self, config: Optional[BedrockConfig] = None) -> None:
        """Initialize Bedrock client with configuration.

        Args:
            config: Optional custom configuration. If not provided, uses default from .env
        """
        self.config = config or default_config

        # Configure AWS client with retry logic and timeouts
        aws_config = Config(
            region_name=self.config.region,
            retries=self.config.get_request_config()
        )

        # Initialize Bedrock client
        try:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                **self.config.get_aws_config(),
                config=aws_config
            )
            logger.info(f"Initialized Bedrock client for region {self.config.region}")
        except Exception as e:
            raise BedrockError("Failed to initialize Bedrock client", cause=e)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[StreamChunk, None]]:
        """Generate text using Claude.

        Args:
            prompt: User input prompt.
            system_prompt: Optional system prompt for context.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.
            stream: Whether to stream the response.

        Returns:
            Generated text or async generator for streaming.

        Raises:
            BedrockError: If generation fails.
        """
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}]
                })
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            })

            # Prepare request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
            }

            if stream:
                response = self.client.invoke_model_with_response_stream(
                    modelId=self.config.model_id,
                    body=json.dumps(request_body),
                    headers=self.config.headers,
                )
                return self._stream_response(response)
            else:
                response = self.client.invoke_model(
                    modelId=self.config.model_id,
                    body=json.dumps(request_body),
                    headers=self.config.headers,
                )
                return self._parse_response(response)

        except Exception as e:
            error_msg = str(e)
            if "ValidationException" in error_msg:
                if "inference profile" in error_msg:
                    raise BedrockError(
                        "AWS Bedrock requires an inference profile. Configure in AWS Console.",
                        cause=e
                    )
                raise BedrockError(f"Invalid request: {error_msg}", cause=e)
            elif "AccessDeniedException" in error_msg:
                raise BedrockError(
                    "Access denied. Verify AWS credentials and permissions.",
                    cause=e
                )
            elif "ResourceNotFoundException" in error_msg:
                raise BedrockError(
                    f"Model {self.config.model_id} not found in {self.config.region}",
                    cause=e
                )
            elif "ThrottlingException" in error_msg:
                raise BedrockError(
                    "Request throttled. Reduce rate or increase quota.",
                    cause=e
                )
            raise BedrockError("Failed to generate response", cause=e)

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[BedrockResponse, AsyncGenerator[StreamChunk, None]]:
        """Have a multi-turn conversation with Claude.

        Args:
            messages: List of conversation messages.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.
            stream: Whether to stream the response.

        Returns:
            Claude's response or stream of response chunks.

        Raises:
            BedrockError: If chat fails.
        """
        try:
            # Convert messages to API format
            api_messages = [
                {
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}]
                }
                for msg in messages
            ]

            # Prepare request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": api_messages,
                "max_tokens": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
            }

            if stream:
                response = self.client.invoke_model_with_response_stream(
                    modelId=self.config.model_id,
                    body=json.dumps(request_body),
                    headers=self.config.headers,
                )
                return self._stream_response(response)
            else:
                response = self.client.invoke_model(
                    modelId=self.config.model_id,
                    body=json.dumps(request_body),
                    headers=self.config.headers,
                )
                return self._parse_response(response)

        except Exception as e:
            raise BedrockError("Failed to process chat", cause=e)

    def _parse_response(self, response: Dict) -> BedrockResponse:
        """Parse non-streaming response.

        Args:
            response: Raw API response.

        Returns:
            Structured response object.

        Raises:
            BedrockError: If response parsing fails.
        """
        try:
            response_body = json.loads(response["body"].read())
            content = response_body["messages"][0]["content"][0]["text"]
            usage = Usage(
                input_tokens=response_body.get("usage", {}).get("input_tokens", 0),
                output_tokens=response_body.get("usage", {}).get("output_tokens", 0),
            )
            return BedrockResponse(
                model_id=self.config.model_id,
                content=content,
                usage=usage
            )
        except Exception as e:
            raise BedrockError("Failed to parse response", cause=e)

    async def _stream_response(
        self,
        response: Dict
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream response chunks.

        Args:
            response: Streaming API response.

        Yields:
            Text and usage chunks as they arrive.

        Raises:
            BedrockError: If streaming fails.
        """
        try:
            async for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                
                if chunk["type"] == "message_start":
                    usage = chunk["message"]["usage"]
                    yield StreamChunk(
                        type="usage",
                        input_tokens=usage.get("input_tokens", 0),
                        output_tokens=usage.get("output_tokens", 0),
                        cache_write_tokens=usage.get("cache_creation_input_tokens"),
                        cache_read_tokens=usage.get("cache_read_input_tokens")
                    )
                
                elif chunk["type"] == "content_block_start":
                    if chunk["content_block"]["type"] == "text":
                        yield StreamChunk(
                            type="text",
                            text=chunk["content_block"]["text"]
                        )
                
                elif chunk["type"] == "content_block_delta":
                    if chunk["delta"]["type"] == "text_delta":
                        yield StreamChunk(
                            type="text",
                            text=chunk["delta"]["text"]
                        )

        except Exception as e:
            raise BedrockError("Failed to stream response", cause=e)