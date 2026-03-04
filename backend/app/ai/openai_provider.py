"""
Rayeva AI — OpenAI-compatible Provider (Azure AI Foundry)
Uses the OpenAI Python SDK pointed at Azure AI endpoint.
Model: grok-4-fast-reasoning (xAI Grok via Azure AI Foundry)
"""

import time
import json
import structlog
from typing import TypeVar, Type, AsyncGenerator, get_args, get_origin
import inspect

import httpx
from openai import AsyncOpenAI, DefaultAsyncHttpxClient
from pydantic import BaseModel

from app.ai.base import AIProvider
from app.ai.models import AIResult
from app.config import get_settings

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)


def _build_example_from_schema(schema: Type[BaseModel]) -> str:
    """
    Build a minimal concrete example JSON from a Pydantic model's fields.
    Prevents models from returning the schema meta-object instead of an instance.
    """
    example: dict = {}
    for field_name, field_info in schema.model_fields.items():
        ann = field_info.annotation
        origin = get_origin(ann)
        args = get_args(ann)

        if origin is list:
            inner = args[0] if args else str
            if inspect.isclass(inner) and issubclass(inner, BaseModel):
                example[field_name] = [json.loads(_build_example_from_schema(inner))]
            elif inner is str or inner is type(None):
                example[field_name] = ["example value"]
            else:
                example[field_name] = [0]
        elif origin is dict:
            example[field_name] = {"example_key": 0.0}
        elif ann is str:
            desc = field_info.description or field_name
            example[field_name] = f"<{desc[:40]}>"
        elif ann is int:
            example[field_name] = 1
        elif ann is float:
            example[field_name] = 0.0
        elif ann is bool:
            example[field_name] = True
        elif inspect.isclass(ann) and issubclass(ann, BaseModel):
            example[field_name] = json.loads(_build_example_from_schema(ann))
        else:
            example[field_name] = None
    return json.dumps(example, indent=2)


class OpenAIProvider(AIProvider):
    """
    OpenAI-compatible provider using the OpenAI Python SDK.
    Targets Azure AI Foundry endpoint.
    Structured output is achieved via JSON mode + schema injection into system prompt.
    """

    def __init__(self):
        settings = get_settings()
        # Use the SDK's built-in timeout — 5 min read for slow reasoning models.
        # DefaultAsyncHttpxClient preserves the SDK's auth/retry/base_url wiring.
        self.client = AsyncOpenAI(
            base_url=settings.azure_ai_endpoint,
            api_key=settings.openai_api_key,
            timeout=httpx.Timeout(connect=10.0, read=300.0, write=30.0, pool=10.0),
        )
        self.model = settings.ai_model
        logger.info("openai_provider_initialized", model=self.model, endpoint=settings.azure_ai_endpoint)

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
        Structured JSON generation via JSON mode + schema injection.
        The Pydantic schema is embedded into the system prompt so the model
        knows exactly what fields and types to produce.
        """
        start_time = time.time()

        # Inject the Pydantic JSON schema into the system prompt
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        example_json = _build_example_from_schema(output_schema)
        system_with_schema = (
            f"{system_prompt}\n\n"
            f"## OUTPUT FORMAT\n"
            f"You MUST return a single JSON object as a concrete DATA INSTANCE.\n"
            f"DO NOT return the schema definition or any meta object (no 'description', 'type', 'properties' keys at the top level).\n\n"
            f"### Field schema (for reference only — do NOT copy this as output):\n"
            f"```json\n{schema_json}\n```\n\n"
            f"### Example of the CORRECT output structure (replace angle-bracket placeholders with real values):\n"
            f"```json\n{example_json}\n```\n\n"
            f"CRITICAL: Return ONLY a single valid JSON object with real data values. "
            f"No markdown fences, no explanations, no extra keys. Pure JSON only."
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_with_schema},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_output_tokens,
            top_p=0.95,
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)
        raw_text = response.choices[0].message.content or ""

        # Token usage
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        # Parse with Pydantic
        parsed = output_schema.model_validate_json(raw_text)

        logger.info(
            "openai_generate_success",
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )

        return AIResult(
            parsed=parsed,
            raw_json=raw_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thinking_tokens=0,
            latency_ms=latency_ms,
            model=self.model,
            provider="openai",
        )

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        thinking_level: str = "LOW",
    ) -> AsyncGenerator[str, None]:
        """
        Streaming free-text generation using OpenAI streaming.
        Yields text chunks as they arrive.
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=temperature,
            top_p=0.95,
            max_tokens=65535,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
