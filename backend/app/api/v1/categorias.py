from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import sesion_db
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.schemas.responses import (
    CategoriaListaRespuesta,
    CategoriaOperacionRespuesta,
)
from app.services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=CategoriaListaRespuesta, summary="Listar categorias")
async def listar_categorias(
    solo_activas: bool = Query(False, description="Omitir las categorias desactivadas"),
    session: AsyncSession = Depends(sesion_db),
) -> CategoriaListaRespuesta:
    service = CategoriaService(session)
    categorias = await service.listar_con_conteo(solo_activas=solo_activas)
    return CategoriaListaRespuesta(
        success=True,
        message=f"{len(categorias)} categoria(s)",
        data=categorias,
    )


@router.post(
    "",
    response_model=CategoriaOperacionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoria",
)
async def crear_categoria(
    payload: CategoriaCreate,
    session: AsyncSession = Depends(sesion_db),
) -> CategoriaOperacionRespuesta:
    service = CategoriaService(session)
    categoria = await service.crear(payload)
    return CategoriaOperacionRespuesta(
        success=True,
        message="Categoria creada correctamente",
        data=CategoriaRead.model_validate(categoria),
    )


@router.put(
    "/{categoria_id}",
    response_model=CategoriaOperacionRespuesta,
    summary="Modificar una categoria",
)
async def actualizar_categoria(
    categoria_id: int,
    payload: CategoriaUpdate,
    session: AsyncSession = Depends(sesion_db),
) -> CategoriaOperacionRespuesta:
    service = CategoriaService(session)
    categoria = await service.actualizar(categoria_id, payload)
    cantidad = await service.cantidad_gastos(categoria_id)
    data = CategoriaRead.model_validate(categoria)
    data.cantidad_gastos = cantidad
    return CategoriaOperacionRespuesta(
        success=True,
        message="Categoria actualizada correctamente",
        data=data,
    )


@router.delete(
    "/{categoria_id}",
    response_model=CategoriaOperacionRespuesta,
    summary="Eliminar una categoria",
    description=(
        "Si la categoria tiene gastos o reglas asociados se debe indicar "
        "`reemplazar_por` con el id de la categoria destino; de lo contrario "
        "responde 409."
    ),
)
async def eliminar_categoria(
    categoria_id: int,
    reemplazar_por: int | None = Query(
        None,
        gt=0,
        description="Categoria destino para reasignar gastos y reglas antes de eliminar",
    ),
    session: AsyncSession = Depends(sesion_db),
) -> CategoriaOperacionRespuesta:
    service = CategoriaService(session)
    categoria = await service.obtener(categoria_id)
    data = CategoriaRead.model_validate(categoria)
    await service.eliminar(categoria_id, reemplazar_por=reemplazar_por)
    return CategoriaOperacionRespuesta(
        success=True,
        message="Categoria eliminada correctamente",
        data=data,
    )
