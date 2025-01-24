"""
FastAPI routes for LLM operations.

This module provides REST API endpoints for interacting with AWS Bedrock
through the LLM service layer.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...bedrock.models import Message
from ...services.llm_service import LLMService, BedrockError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/llm", tags=["llm"])

# Initialize service
llm_service = LLMService()


class GenerateRequest(BaseModel):
    """Request model for text generation."""
    prompt: str = Field(..., description="Input prompt")
    system_prompt: Optional[str] = Field(None, description="System context")
    temperature: Optional[float] = Field(None, description="Temperature (0.0 to 1.0)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    use_cache: bool = Field(True, description="Whether to use response caching")


class ChatRequest(BaseModel):
    """Request model for chat conversation."""
    messages: List[Message] = Field(..., description="Conversation messages")
    temperature: Optional[float] = Field(None, description="Temperature (0.0 to 1.0)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    stream: bool = Field(False, description="Whether to stream the response")


class CodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code: str = Field(..., description="Code to analyze")
    context: Optional[str] = Field(None, description="Additional context")


class SummarizeRequest(BaseModel):
    """Request model for text summarization."""
    text: str = Field(..., description="Text to summarize")
    max_length: Optional[int] = Field(None, description="Maximum summary length")
    format: str = Field("bullet_points", description="Output format")


@router.post("/generate")
async def generate_text(request: GenerateRequest):
    """Generate text using Claude."""
    try:
        response = await llm_service.generate_text(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_cache=request.use_cache
        )
        return {"response": response}
    except BedrockError as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest):
    """Have a conversation with Claude."""
    try:
        response = await llm_service.chat(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )
        
        if request.stream:
            # Return StreamingResponse for streaming
            return response
        else:
            # Return normal response
            return response.dict()
            
    except BedrockError as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-code")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code and provide suggestions."""
    try:
        analysis = await llm_service.analyze_code(
            code=request.code,
            context=request.context
        )
        return analysis
    except BedrockError as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """Summarize text content."""
    try:
        summary = await llm_service.summarize_text(
            text=request.text,
            max_length=request.max_length,
            format=request.format
        )
        return {"summary": summary}
    except BedrockError as e:
        logger.error(f"Text summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Ejemplo de uso:
"""
# Generar texto
curl -X POST "http://localhost:8000/api/llm/generate" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Explica la programación asíncrona"}'

# Chat
curl -X POST "http://localhost:8000/api/llm/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "messages": [
            {"role": "user", "content": "¿Qué es Python?"}
        ]
    }'

# Analizar código
curl -X POST "http://localhost:8000/api/llm/analyze-code" \
    -H "Content-Type: application/json" \
    -d '{
        "code": "def suma(a, b):\\n    return a + b"
    }'

# Resumir texto
curl -X POST "http://localhost:8000/api/llm/summarize" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "Lorem ipsum...",
        "format": "bullet_points"
    }'
"""