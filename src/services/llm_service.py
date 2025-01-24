"""
High-level service for LLM operations using AWS Bedrock.

This module provides a service layer that abstracts common LLM operations
and implements caching, retry logic, and error handling.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from ..bedrock.client import BedrockClient, BedrockError
from ..bedrock.config import BedrockConfig
from ..bedrock.models import Message, StreamChunk, BedrockResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Service for handling LLM operations."""

    def __init__(self, config: Optional[BedrockConfig] = None):
        """Initialize service with optional custom configuration."""
        self.client = BedrockClient(config)
        self._response_cache: Dict[str, str] = {}

    def _cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for a request."""
        cache_dict = {
            "prompt": prompt,
            **kwargs
        }
        return json.dumps(cache_dict, sort_keys=True)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True
    ) -> str:
        """Generate text response.

        Args:
            prompt: User input prompt.
            system_prompt: Optional system context.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.
            use_cache: Whether to use response caching.

        Returns:
            Generated text response.

        Raises:
            BedrockError: If generation fails.
        """
        try:
            # Check cache
            if use_cache:
                cache_key = self._cache_key(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                if cache_key in self._response_cache:
                    logger.info("Cache hit for prompt")
                    return self._response_cache[cache_key]

            # Generate response
            response = await self.client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Cache response
            if use_cache and isinstance(response, str):
                self._response_cache[cache_key] = response

            return response

        except BedrockError as e:
            logger.error(f"Text generation failed: {e}")
            raise

    async def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[BedrockResponse, AsyncGenerator[StreamChunk, None]]:
        """Have a conversation.

        Args:
            messages: Conversation messages.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.
            stream: Whether to stream the response.

        Returns:
            Chat response or stream of response chunks.

        Raises:
            BedrockError: If chat fails.
        """
        try:
            return await self.client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
        except BedrockError as e:
            logger.error(f"Chat failed: {e}")
            raise

    async def analyze_code(
        self,
        code: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze code and provide suggestions.

        Args:
            code: Code to analyze.
            context: Optional context about the code.

        Returns:
            Analysis results including suggestions and issues.

        Raises:
            BedrockError: If analysis fails.
        """
        try:
            system_prompt = """
            You are an expert code reviewer. Analyze the provided code and return a JSON response with:
            - issues: List of potential issues found
            - suggestions: List of improvement suggestions
            - best_practices: List of relevant best practices
            - security_concerns: List of security considerations
            """

            prompt = f"""
            Code to analyze:
            ```
            {code}
            ```
            """
            if context:
                prompt += f"\nContext: {context}"

            response = await self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1  # Lower temperature for more consistent analysis
            )

            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.error("Failed to parse analysis response as JSON")
                return {
                    "error": "Failed to parse analysis",
                    "raw_response": response
                }

        except BedrockError as e:
            logger.error(f"Code analysis failed: {e}")
            raise

    async def summarize_text(
        self,
        text: str,
        max_length: Optional[int] = None,
        format: str = "bullet_points"
    ) -> str:
        """Summarize text content.

        Args:
            text: Text to summarize.
            max_length: Optional maximum length for summary.
            format: Output format (paragraph, bullet_points).

        Returns:
            Generated summary.

        Raises:
            BedrockError: If summarization fails.
        """
        try:
            format_prompt = {
                "paragraph": "Provide a concise paragraph summary.",
                "bullet_points": "Provide a bullet-point summary with key points."
            }.get(format, "Provide a summary.")

            system_prompt = f"""
            You are a skilled summarizer. {format_prompt}
            Keep the summary clear and informative.
            """

            if max_length:
                system_prompt += f" Limit the summary to approximately {max_length} words."

            response = await self.generate_text(
                prompt=text,
                system_prompt=system_prompt,
                temperature=0.3  # Moderate temperature for balance
            )

            return response

        except BedrockError as e:
            logger.error(f"Text summarization failed: {e}")
            raise