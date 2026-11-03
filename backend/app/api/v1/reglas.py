from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import sesion_db
from app.schemas.regla import ReglaCreate, ReglaRead, ReglaUpdate
from app.schemas.responses import ReglaListaRespuesta, ReglaOperacionRespuesta
from app.services.regla_service import ReglaService

router = APIRouter(prefix="/reglas", tags=["Reglas"])


@router.get("", response_model=ReglaListaRespuesta, summary="Listar reglas")
async def listar_reglas(
    solo_activas: bool = Query(False, description="Omitir las reglas desactivadas"),
    session: AsyncSession = Depends(sesion_db),
) -> ReglaListaRespuesta:
    service = ReglaService(session)
    reglas = await service.listar(solo_activas=solo_activas)
    return ReglaListaRespuesta(
        success=True,
        message=f"{len(reglas)} regla(s)",
        data=[ReglaRead.model_validate(regla) for regla in reglas],
    )


@router.post(
    "",
    response_model=ReglaOperacionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una regla de categorizacion",
)
async def crear_regla(
    payload: ReglaCreate,
    session: AsyncSession = Depends(sesion_db),
) -> ReglaOperacionRespuesta:
    service = ReglaService(session)
    regla = await service.crear(payload)
    return ReglaOperacionRespuesta(
        success=True,
        message="Regla creada correctamente",
        data=ReglaRead.model_validate(regla),
    )


@router.put(
    "/{regla_id}",
    response_model=ReglaOperacionRespuesta,
    summary="Modificar una regla",
)
async def actualizar_regla(
    regla_id: int,
    payload: ReglaUpdate,
    session: AsyncSession = Depends(sesion_db),
) -> ReglaOperacionRespuesta:
    service = ReglaService(session)
    regla = await service.actualizar(regla_id, payload)
    return ReglaOperacionRespuesta(
        success=True,
        message="Regla actualizada correctamente",
        data=ReglaRead.model_validate(regla),
    )


@router.delete(
    "/{regla_id}",
    response_model=ReglaOperacionRespuesta,
    summary="Eliminar una regla",
)
async def eliminar_regla(
    regla_id: int,
    session: AsyncSession = Depends(sesion_db),
) -> ReglaOperacionRespuesta:
    service = ReglaService(session)
    regla = await service.obtener(regla_id)
    data = ReglaRead.model_validate(regla)
    await service.eliminar(regla_id)
    return ReglaOperacionRespuesta(
        success=True,
        message="Regla eliminada correctamente",
        data=data,
    )
