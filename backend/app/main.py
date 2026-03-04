"""
Rayeva AI — FastAPI Application Entry Point
AI-Powered Modules for Sustainable Commerce.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.middleware import CorrelationIDMiddleware
from app.api.v1.category import router as category_router
from app.api.v1.proposals import router as proposals_router
from app.api.v1.logs import router as logs_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed data. Shutdown: cleanup."""
    structlog.get_logger().info("app_starting", app=settings.app_name)
    init_db()

    # Seed predefined categories
    from app.database import SessionLocal
    from app.models.category import Category, PREDEFINED_CATEGORIES
    db = SessionLocal()
    try:
        if db.query(Category).count() == 0:
            for cat in PREDEFINED_CATEGORIES:
                db.add(Category(**cat))
            db.commit()
            structlog.get_logger().info("categories_seeded", count=len(PREDEFINED_CATEGORIES))
    finally:
        db.close()

    yield  # App is running
    structlog.get_logger().info("app_shutting_down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered modules for sustainable commerce: "
        "Auto-categorization, B2B proposal generation, impact reporting, and more."
    ),
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIDMiddleware)

# Routers
app.include_router(category_router)
app.include_router(proposals_router)
app.include_router(logs_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "modules": {
            "module_1": "AI Auto-Category & Tag Generator — /api/v1/categorize",
            "module_2": "AI B2B Proposal Generator — /api/v1/proposals/generate",
            "logs": "AI Call Logs — /api/v1/logs",
            "metrics": "Dashboard Metrics — /api/v1/metrics",
        },
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
