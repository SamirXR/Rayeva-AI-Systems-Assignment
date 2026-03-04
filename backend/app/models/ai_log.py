"""
Rayeva AI — AI Log SQLAlchemy Model
Every AI call is logged: prompt version, tokens, latency, raw I/O.
Satisfies Technical Requirement #2: Prompt + response logging.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, func
from app.database import Base


class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    correlation_id = Column(String(36), nullable=True, index=True)
    module = Column(String(50), nullable=False)  # "category", "proposal", etc.
    prompt_version = Column(String(20), nullable=False)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), default="gemini")

    # Token usage
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    thinking_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)

    # Raw I/O for debugging
    raw_input = Column(JSON, nullable=True)   # the prompt sent
    raw_output = Column(JSON, nullable=True)  # the raw AI response

    # Outcome
    parsed_success = Column(Boolean, default=True)
    error = Column(String(1000), nullable=True)
    cost_usd = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
