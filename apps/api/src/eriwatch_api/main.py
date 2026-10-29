"""FastAPI application entry point for EriWatch."""

import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from eriwatch_api.config import Settings, get_settings
from eriwatch_api.logging_config import configure_logging

logger = logging.getLogger("eriwatch.api")


class HealthResponse(BaseModel):
    """Schema for the /health endpoint response."""

    status: str
    service: str
    version: str
    environment: str
    timestamp: str


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Configure logging and startup/shutdown hooks."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info(
        "Starting %s v%s (%s)",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    cfg = settings or get_settings()
    configure_logging(cfg.log_level)

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description=(
            "Satellite-Based Early Warning and Grievance Platform for "
            "Village Irrigation Tanks (Eris) in Tamil Nadu."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def attach_request_id(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health_check() -> HealthResponse:
        """Return service health status and metadata."""
        return HealthResponse(
            status="ok",
            service=cfg.app_name,
            version=cfg.app_version,
            environment=cfg.environment,
            timestamp=datetime.now(UTC).isoformat(),
        )

    return app


app = create_app()
