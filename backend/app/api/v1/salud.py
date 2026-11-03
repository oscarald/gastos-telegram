from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import sesion_db
from app.core.config import get_settings
from app.schemas.common import HealthRespuesta

router = APIRouter(tags=["Sistema"])


@router.get("/health", response_model=HealthRespuesta, summary="Estado de la aplicacion")
async def health(session: AsyncSession = Depends(sesion_db)) -> HealthRespuesta:
    settings = get_settings()
    estado_bd = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - depende del estado de la base de datos
        estado_bd = "error"
    return HealthRespuesta(
        status="ok" if estado_bd == "ok" else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        database=estado_bd,
        timezone=settings.app_timezone,
    )
