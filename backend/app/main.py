from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.db.session import dispose_engine

API_PREFIX = "/api/v1"

DESCRIPTION = """
API REST del sistema de control de gastos personales.

* `POST /api/v1/gastos/telegram` es el endpoint de integracion con n8n (requiere `X-API-Key`).
* El resto de endpoints lo consume el dashboard web.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(api_router, prefix=API_PREFIX)

    @application.get("/", include_in_schema=False)
    async def raiz() -> dict[str, str]:
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "api": API_PREFIX,
        }

    return application


app = create_app()
