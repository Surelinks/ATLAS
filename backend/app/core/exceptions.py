"""
Atlas AI - Centralised Exception Handlers
==========================================
Defines application-wide custom exceptions and FastAPI exception handlers
so every error surface returns a consistent JSON envelope.

Response envelope::

    {
        "error":   "Human-readable summary",
        "detail":  "Technical detail or list of validation errors",
        "code":    "MACHINE_READABLE_CODE",
        "request_id": "<uuid>"          # present when middleware is active
    }

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exception hierarchy
# ---------------------------------------------------------------------------


class AtlasBaseError(Exception):
    """Root exception for all Atlas AI application errors."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class DocumentProcessingError(AtlasBaseError):
    """Raised when a document cannot be parsed or chunked."""

    status_code = 422
    code = "DOCUMENT_PROCESSING_ERROR"
    message = "Failed to process the uploaded document."


class LLMProviderError(AtlasBaseError):
    """Raised when the LLM backend is unavailable or returns an error."""

    status_code = 503
    code = "LLM_PROVIDER_ERROR"
    message = "The language model provider is currently unavailable."


class VectorStoreError(AtlasBaseError):
    """Raised when the vector store operation fails."""

    status_code = 500
    code = "VECTOR_STORE_ERROR"
    message = "A vector store operation failed."


class DocumentNotFoundError(AtlasBaseError):
    """Raised when a requested document does not exist in the store."""

    status_code = 404
    code = "DOCUMENT_NOT_FOUND"
    message = "The requested document was not found."


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _request_id(request: Request) -> str | None:
    return getattr(getattr(request, "state", None), "request_id", None)


def _envelope(
    error: str,
    detail: Any,
    code: str,
    request_id: str | None,
) -> dict:
    payload: dict = {"error": error, "detail": detail, "code": code}
    if request_id:
        payload["request_id"] = request_id
    return payload


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------


async def atlas_exception_handler(request: Request, exc: AtlasBaseError) -> JSONResponse:
    """Handler for all Atlas-specific application exceptions."""
    logger.error(
        "AtlasError | code=%s request_id=%s message=%s",
        exc.code,
        _request_id(request),
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(
            error=exc.message,
            detail=exc.message,
            code=exc.code,
            request_id=_request_id(request),
        ),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handler for standard HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(
            error=str(exc.detail),
            detail=str(exc.detail),
            code=f"HTTP_{exc.status_code}",
            request_id=_request_id(request),
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic request-validation errors."""
    logger.warning(
        "Validation error | request_id=%s errors=%s",
        _request_id(request),
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=_envelope(
            error="Request validation failed.",
            detail=exc.errors(),
            code="VALIDATION_ERROR",
            request_id=_request_id(request),
        ),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler so unexpected exceptions never expose a stack trace."""
    logger.exception(
        "Unhandled exception | request_id=%s", _request_id(request)
    )
    return JSONResponse(
        status_code=500,
        content=_envelope(
            error="An internal server error occurred.",
            detail="Contact the system administrator if this persists.",
            code="INTERNAL_ERROR",
            request_id=_request_id(request),
        ),
    )
