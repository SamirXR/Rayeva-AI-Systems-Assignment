"""
Rayeva AI — Proposal SQLAlchemy Model
B2B proposals with AI-generated product mix, budget, and impact data.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
from app.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Client input
    client_name = Column(String(200), nullable=False)
    budget = Column(Float, nullable=False)
    category_preferences = Column(JSON, nullable=True)  # list[str]
    sustainability_goals = Column(JSON, nullable=True)  # list[str]
    occasion = Column(String(200), nullable=True)
    quantity_min = Column(Integer, nullable=True)
    quantity_max = Column(Integer, nullable=True)
    special_requirements = Column(String(1000), nullable=True)

    # AI-generated fields
    product_mix = Column(JSON, nullable=True)  # list[dict]
    budget_allocation = Column(JSON, nullable=True)  # dict
    cost_breakdown = Column(JSON, nullable=True)  # dict
    impact_summary = Column(JSON, nullable=True)  # dict
    status = Column(String(50), default="generated")

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
