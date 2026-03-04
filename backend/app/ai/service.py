"""
Rayeva AI — AI Service Orchestrator
Handles retry logic, Pydantic validation fallback, and AI call logging.
This is the ONLY layer business logic should interact with.
"""

import json
import structlog
from typing import TypeVar, Type, Optional

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.ai.base import AIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.models import AIResult, AIError
from app.models.ai_log import AILog
from app.config import get_settings

logger = structlog.get_logger()
T = TypeVar("T", bound=BaseModel)

# Singleton provider instance
_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """Factory: returns the configured AI provider. Currently OpenAI (Azure AI Foundry / Grok)."""
    global _provider
    if _provider is None:
        _provider = OpenAIProvider()
    return _provider


class AIService:
    """
    Orchestrates AI calls with:
    - Retry logic (up to N retries with error context injection)
    - Pydantic validation with fallback
    - Automatic logging to ai_logs table
    """

    def __init__(self, db: Session, correlation_id: str = ""):
        self.provider = get_ai_provider()
        self.db = db
        self.correlation_id = correlation_id
        self.settings = get_settings()

    async def generate(
        self,
        module: str,
        prompt_version: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: Type[T],
        temperature: Optional[float] = None,
        thinking_level: Optional[str] = None,
    ) -> AIResult[T]:
        """
        Generate structured AI output with retry logic and logging.

        Args:
            module: Which module is calling ("category", "proposal", etc.)
            prompt_version: Version tag for the prompt (e.g., "v1")
            system_prompt: System instruction
            user_prompt: User input
            output_schema: Pydantic model class for structured output
            temperature: Override default (None = use config default for structured)
            thinking_level: Override default (None = use config default)

        Returns:
            AIResult[T] with parsed output and metadata
        """
        temp = temperature if temperature is not None else self.settings.ai_temperature_structured
        think = thinking_level if thinking_level is not None else self.settings.ai_thinking_level
        max_retries = self.settings.ai_max_retries
        last_error: Optional[str] = None

        for attempt in range(max_retries + 1):
            try:
                # On retry, inject the error into the prompt for self-correction
                effective_user_prompt = user_prompt
                if attempt > 0 and last_error:
                    effective_user_prompt = (
                        f"{user_prompt}\n\n"
                        f"[RETRY {attempt}/{max_retries}] Previous attempt failed: {last_error}. "
                        f"Please ensure your response strictly follows the required JSON schema."
                    )

                result: AIResult[T] = await self.provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=effective_user_prompt,
                    output_schema=output_schema,
                    temperature=temp,
                    thinking_level=think,
                    max_output_tokens=self.settings.ai_max_output_tokens,
                )
                result.prompt_version = prompt_version

                # Log successful call
                self._log_call(
                    module=module,
                    prompt_version=prompt_version,
                    result=result,
                    raw_input={"system": system_prompt[:500], "user": user_prompt[:500]},
                    parsed_success=True,
                )

                return result

            except ValidationError as e:
                last_error = f"Pydantic validation: {str(e)[:300]}"
                logger.warning(
                    "ai_validation_error",
                    module=module,
                    attempt=attempt + 1,
                    error=last_error,
                )

            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)[:300]}"
                logger.error(
                    "ai_call_error",
                    module=module,
                    attempt=attempt + 1,
                    error=last_error,
                )

        # All retries exhausted — log failure and raise
        self._log_call(
            module=module,
            prompt_version=prompt_version,
            result=None,
            raw_input={"system": system_prompt[:500], "user": user_prompt[:500]},
            parsed_success=False,
            error=last_error,
        )
        raise RuntimeError(
            f"AI call failed after {max_retries + 1} attempts for module '{module}': {last_error}"
        )

    def _log_call(
        self,
        module: str,
        prompt_version: str,
        result: Optional[AIResult],
        raw_input: dict,
        parsed_success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Persist AI call details to the ai_logs table."""
        try:
            log_entry = AILog(
                correlation_id=self.correlation_id,
                module=module,
                prompt_version=prompt_version,
                model=result.model if result else self.settings.ai_model,
                provider=result.provider if result else "openai",
                input_tokens=result.input_tokens if result else 0,
                output_tokens=result.output_tokens if result else 0,
                thinking_tokens=result.thinking_tokens if result else 0,
                latency_ms=result.latency_ms if result else 0,
                raw_input=raw_input,
                raw_output=json.loads(result.raw_json) if result and result.raw_json else None,
                parsed_success=parsed_success,
                error=error,
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as log_err:
            logger.error("ai_log_write_failed", error=str(log_err))
