"""
Rayeva AI — Product SQLAlchemy Model
Products with AI-generated categories, tags, and sustainability filters.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=False)
    price = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)

    # AI-generated fields
    primary_category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    category_confidence = Column(Float, nullable=True)
    seo_tags = Column(JSON, nullable=True)  # list[str]
    sustainability_filters = Column(JSON, nullable=True)  # list[str]
    detected_materials = Column(JSON, nullable=True)  # list[str]
    sustainability_score = Column(Float, nullable=True)
    ai_metadata = Column(JSON, nullable=True)  # full AI response metadata

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    categorized_at = Column(DateTime, nullable=True)
