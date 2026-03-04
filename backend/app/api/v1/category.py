"""
Rayeva AI — Category API Endpoints (Module 1)
Auto-categorize products with AI-generated tags, sustainability filters, and scoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.category import (
    ProductInput,
    ProductCategorizationResponse,
    BatchCategorizationRequest,
    BatchCategorizationResponse,
)
from app.services.category_service import CategoryService
from app.models.category import PREDEFINED_CATEGORIES

router = APIRouter(prefix="/api/v1", tags=["Category & Tags — Module 1"])


@router.post("/categorize", response_model=ProductCategorizationResponse)
async def categorize_product(
    product: ProductInput,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    AI Auto-Category & Tag Generator — Single product.

    Takes a product name + description and returns:
    - Primary category (from predefined list)
    - Sub-category suggestion
    - 5-10 SEO tags
    - Sustainability filters
    - Rules-based sustainability score
    - Stored in database
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    service = CategoryService(db=db, correlation_id=correlation_id)

    try:
        result = await service.categorize_product(product)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")


@router.post("/categorize/batch", response_model=BatchCategorizationResponse)
async def batch_categorize(
    batch: BatchCategorizationRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Batch categorize up to 50 products concurrently.
    Returns individual results with success/failure tracking.
    """
    correlation_id = getattr(request.state, "correlation_id", "")
    service = CategoryService(db=db, correlation_id=correlation_id)

    try:
        results = await service.batch_categorize(batch.products)
        successful = [r for r in results if isinstance(r, ProductCategorizationResponse)]
        failed = [r for r in results if isinstance(r, dict)]

        return BatchCategorizationResponse(
            results=successful,
            total=len(batch.products),
            successful=len(successful),
            failed=len(failed),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch categorization failed: {str(e)}")


@router.get("/categories")
async def list_categories():
    """List all predefined product categories."""
    return {"categories": PREDEFINED_CATEGORIES}


@router.get("/products")
async def list_products(
    category: str | None = None,
    sustainability_filter: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all categorized products with optional filters."""
    query = db.query(Product).filter(Product.primary_category.isnot(None))

    if category:
        query = query.filter(Product.primary_category == category)

    products = query.offset(skip).limit(limit).all()
    total = query.count()

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description[:200],
                "price": p.price,
                "primary_category": p.primary_category,
                "sub_category": p.sub_category,
                "category_confidence": p.category_confidence,
                "seo_tags": p.seo_tags,
                "sustainability_filters": p.sustainability_filters,
                "sustainability_score": p.sustainability_score,
                "created_at": str(p.created_at) if p.created_at else None,
            }
            for p in products
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product with all AI-generated metadata."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "primary_category": product.primary_category,
        "sub_category": product.sub_category,
        "category_confidence": product.category_confidence,
        "seo_tags": product.seo_tags,
        "sustainability_filters": product.sustainability_filters,
        "detected_materials": product.detected_materials,
        "sustainability_score": product.sustainability_score,
        "ai_metadata": product.ai_metadata,
        "created_at": str(product.created_at) if product.created_at else None,
        "categorized_at": str(product.categorized_at) if product.categorized_at else None,
    }
