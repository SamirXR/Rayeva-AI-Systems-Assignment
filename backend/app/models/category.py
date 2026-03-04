"""
Rayeva AI — Category SQLAlchemy Model
Predefined sustainable product categories.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# Predefined categories for the sustainable commerce platform
PREDEFINED_CATEGORIES = [
    {"name": "Home & Living", "slug": "home-living", "description": "Sustainable home décor, furniture, and lifestyle products"},
    {"name": "Personal Care", "slug": "personal-care", "description": "Eco-friendly skincare, haircare, and hygiene products"},
    {"name": "Kitchen & Dining", "slug": "kitchen-dining", "description": "Reusable, biodegradable kitchen and dining essentials"},
    {"name": "Fashion & Accessories", "slug": "fashion-accessories", "description": "Sustainable clothing, bags, and jewelry"},
    {"name": "Stationery & Office", "slug": "stationery-office", "description": "Recycled, plantable, and eco-friendly office supplies"},
    {"name": "Food & Beverages", "slug": "food-beverages", "description": "Organic, locally sourced food and drink products"},
    {"name": "Cleaning & Household", "slug": "cleaning-household", "description": "Non-toxic, biodegradable cleaning products"},
    {"name": "Baby & Kids", "slug": "baby-kids", "description": "Safe, organic, and sustainable products for children"},
    {"name": "Pet Care", "slug": "pet-care", "description": "Eco-friendly pet food, toys, and accessories"},
    {"name": "Garden & Outdoor", "slug": "garden-outdoor", "description": "Sustainable gardening tools, seeds, and outdoor items"},
]
