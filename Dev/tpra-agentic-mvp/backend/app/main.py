"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1 import agents, audit, catalog, files, health, reviewer_log, workspaces
from app.core.config import get_settings
from app.core.exceptions import TPRAError
from app.core.logging import configure_logging, correlation_id_var
from app.domain.models import new_id


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(
        settings.observability.log_level,
        json_logs=settings.observability.json_logs,
    )

    app = FastAPI(
        title="TPRA Agentic MVP API",
        version=__version__,
        description="Human-in-the-loop TPRA agentic platform (UC1 findings + UC2 report).",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        cid = request.headers.get("x-correlation-id") or new_id("corr")
        token = correlation_id_var.set(cid)
        try:
            response = await call_next(request)
            response.headers["x-correlation-id"] = cid
            return response
        finally:
            correlation_id_var.reset(token)

    @app.exception_handler(TPRAError)
    async def tpra_error_handler(_request: Request, exc: TPRAError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(health.router, prefix="/api")
    app.include_router(health.router)  # /health for probes
    app.include_router(catalog.router, prefix="/api")
    app.include_router(workspaces.router, prefix="/api")
    app.include_router(files.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(reviewer_log.router, prefix="/api")
    app.include_router(audit.router, prefix="/api")

    @app.get("/")
    def root():
        return {
            "name": "TPRA Agentic MVP",
            "version": __version__,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


app = create_app()
