"""
Rayeva AI — AI Result & Base Models
Generic result type returned by every AI call.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Any, Optional

T = TypeVar("T")


@dataclass
class AIResult(Generic[T]):
    """
    Every AI call returns this wrapper.
    Contains the parsed output + metadata for logging/debugging.
    """
    parsed: T
    raw_json: str
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""
    prompt_version: str = ""
    provider: str = "gemini"
    cached: bool = False


@dataclass
class AIError:
    """Structured error when AI call fails after all retries."""
    error_type: str  # "parse_error", "api_error", "validation_error", "timeout"
    message: str
    raw_response: Optional[str] = None
    retries_attempted: int = 0
