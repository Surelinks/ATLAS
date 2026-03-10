"""
Atlas AI - Health & Readiness Endpoints
=========================================
Provides ``/health`` (liveness) and ``/ready`` (readiness) probes used by
Render, Docker, and Kubernetes to determine whether the service is alive
and capable of serving traffic.

Author  : Ezenwanne Kenneth
Project : Atlas AI – Operational Intelligence & Incident Response Platform
Version : 1.0.0
License : MIT
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Liveness probe", tags=["Health"])
async def health_check() -> dict:
    """
    Liveness probe – confirms the process is running.

    Returns HTTP 200 as long as the application has started successfully.
    Orchestrators (Render, Docker, K8s) use this to decide whether to
    restart the container.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", summary="Readiness probe", tags=["Health"])
async def readiness_check() -> dict:
    """
    Readiness probe – confirms the service can handle requests.

    Actively checks critical dependencies (vector store, LLM provider)
    and returns HTTP 200 only when all checks pass.
    """
    checks: dict = {}
    overall = "ready"

    # -- Vector store --------------------------------------------------
    try:
        from app.services.simple_vector_store import vector_store  # noqa: PLC0415

        stats = vector_store.get_stats()
        checks["vector_store"] = (
            f"ok ({stats['total_documents']} docs, {stats['total_chunks']} chunks)"
        )
    except Exception as exc:
        checks["vector_store"] = f"error: {exc}"
        overall = "degraded"

    # -- LLM provider --------------------------------------------------
    try:
        provider = settings.LLM_PROVIDER.lower()
        if provider == "groq" and not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured")
        if provider == "openai" and not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        checks["llm_provider"] = f"ok (provider={provider}, model={_active_model()})"
    except Exception as exc:
        checks["llm_provider"] = f"error: {exc}"
        overall = "degraded"

    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


def _active_model() -> str:
    """Return the configured LLM model name."""
    p = settings.LLM_PROVIDER.lower()
    if p == "groq":
        return settings.GROQ_MODEL
    if p == "openai":
        return settings.OPENAI_MODEL
    return settings.OLLAMA_MODEL
