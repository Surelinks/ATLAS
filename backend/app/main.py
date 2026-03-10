"""
Atlas AI - Main FastAPI Application
=====================================
Operational Intelligence & Incident Response Platform for 330kV/132kV substations.

This module bootstraps the FastAPI application, registers middleware, exception
handlers, and API routers.  It is the single entry-point for the backend service.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import health, ops_copilot
from app.core.config import settings
from app.core.exceptions import (
    AtlasBaseError,
    atlas_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.middleware import RequestLoggingMiddleware

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application start-up and shutdown hooks."""
    logger.info(
        "Starting Atlas AI v%s | environment=%s",
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Atlas AI shutting down gracefully.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered platform for operational intelligence and incident response "
        "in 330kV/132kV power substations. "
        "Features RAG-based SOP assistant, SCADA telemetry, and root-cause analysis."
    ),
    contact={
        "name": "Ezenwanne Kenneth",
        "email": "ezenwannekenneth@gmail.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware  (order matters: last-added is executed first)
# ---------------------------------------------------------------------------

# CORS – allow all origins in production; restrict in development via env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging + request-ID injection
app.add_middleware(RequestLoggingMiddleware)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(AtlasBaseError, atlas_exception_handler)          # type: ignore[arg-type]
app.add_exception_handler(StarletteHTTPException, http_exception_handler)   # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)           # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router, tags=["Health"])
app.include_router(
    ops_copilot.router,
    prefix="/api/v1/ops-copilot",
    tags=["Ops Copilot"],
)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@app.get("/", tags=["Root"], summary="API root")
async def root() -> dict:
    """Returns a welcome message and links to interactive documentation."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "author": "Ezenwanne Kenneth",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Dev runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
