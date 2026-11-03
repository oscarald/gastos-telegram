from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_api_key
from app.db.session import get_db


async def sesion_db(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    """Sesion de base de datos para los endpoints."""
    return db


async def requiere_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Exige una API Key valida (integracion n8n / Telegram)."""
    verify_api_key(x_api_key)
