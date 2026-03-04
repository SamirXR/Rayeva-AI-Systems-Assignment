"""
Rayeva AI — Abstract AI Provider
Interface for all AI providers. Swap Gemini → OpenAI → Groq by implementing this.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

from app.ai.models import AIResult

T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    Ensures clean separation: business logic never touches SDK-specific code.
    """

    @abstractmethod
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
        Generate a structured response from the AI model.

        Args:
            system_prompt: System instruction (role, context, rules)
            user_prompt: User input (product description, client requirements, etc.)
            output_schema: Pydantic model class — enforced via constrained decoding
            temperature: 0.0-1.0 (lower = more deterministic)
            thinking_level: "NONE", "LOW", "MEDIUM", "HIGH"
            max_output_tokens: Max tokens in response

        Returns:
            AIResult[T] with parsed Pydantic model + metadata
        """
        ...

    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        thinking_level: str = "LOW",
    ):
        """
        Stream a free-text response (for chatbot / narrative generation).
        Yields text chunks.
        """
        ...
