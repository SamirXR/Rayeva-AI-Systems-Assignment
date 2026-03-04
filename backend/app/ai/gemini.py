"""
Rayeva AI — Gemini Provider
Concrete implementation using google-genai SDK.
Based on the user's exact SDK pattern with gemini-3.1-flash-lite-preview.
"""

import time
import json
import structlog
from typing import TypeVar, Type, AsyncGenerator

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.ai.base import AIProvider
from app.ai.models import AIResult, AIError
from app.config import get_settings

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProvider):
    """
    Google Gemini provider using google-genai SDK.
    Supports structured JSON output via response_schema (constrained decoding).
    """

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(
            vertexai=True,
            api_key=settings.google_cloud_api_key,
        )
        self.model = settings.ai_model
        logger.info("gemini_provider_initialized", model=self.model)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[T],
        temperature: float = 0.3,
        thinking_level: str = "LOW",
        max_output_tokens: int = 8192,
    ) -> AIResult[T]:
        """
        Non-streaming structured JSON generation.
        Uses response_schema for server-side constrained decoding.
        """
        start_time = time.time()

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            top_p=0.95,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
            response_schema=output_schema,
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
            ],
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_prompt)],
            )
        ]

        # Synchronous call (google-genai uses sync by default)
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)
        raw_text = response.text or ""

        # Extract token usage from response metadata
        usage = response.usage_metadata if hasattr(response, "usage_metadata") and response.usage_metadata else None
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0
        thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0

        # Parse with Pydantic — schema was enforced at decoding time
        parsed = output_schema.model_validate_json(raw_text)

        logger.info(
            "gemini_generate_success",
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
            latency_ms=latency_ms,
        )

        return AIResult(
            parsed=parsed,
            raw_json=raw_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=thinking_tokens,
            latency_ms=latency_ms,
            model=self.model,
            provider="gemini",
        )

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        thinking_level: str = "LOW",
    ) -> AsyncGenerator[str, None]:
        """
        Streaming free-text generation (for chat/narrative).
        Yields text chunks as they arrive.
        """
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            top_p=0.95,
            max_output_tokens=65535,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
            ],
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_prompt)],
            )
        ]

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        ):
            if (
                not chunk.candidates
                or not chunk.candidates[0].content
                or not chunk.candidates[0].content.parts
            ):
                continue
            yield chunk.text
