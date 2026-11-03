from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import requiere_api_key, sesion_db
from app.schemas.gasto import (
    GastoCreate,
    GastoPaginado,
    GastoRead,
    GastoTelegramCreate,
    GastoUpdate,
)
from app.schemas.responses import (
    GastoOperacionRespuesta,
    GastoPaginadoRespuesta,
    GastoTelegramRespuesta,
)
from app.services.export_service import gastos_a_csv
from app.services.gasto_service import GastoService

router = APIRouter(prefix="/gastos", tags=["Gastos"])

OrdenGasto = Literal["fecha_asc", "fecha_desc", "monto_asc", "monto_desc", "categoria_asc"]


def _filtros(
    service: GastoService,
    mes: int | None,
    anio: int | None,
    fecha_desde: str | None,
    fecha_hasta: str | None,
    categoria_id: int | None,
    metodo_pago: str | None,
    origen: str | None,
    busqueda: str | None,
):
    return service.construir_filtros(
        mes=mes,
        anio=anio,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria_id=categoria_id,
        metodo_pago=metodo_pago,
        origen=origen,
        busqueda=busqueda,
    )


@router.post(
    "/telegram",
    response_model=GastoTelegramRespuesta,
    status_code=status.HTTP_200_OK,
    summary="Registrar un gasto proveniente de Telegram",
    description=(
        "Endpoint de integracion. Requiere la cabecera `X-API-Key` con el valor de "
        "`N8N_API_KEY`. Si el `identificador_externo` ya existe devuelve el gasto "
        "original con `duplicate: true` y no crea un registro nuevo."
    ),
)
async def registrar_desde_telegram(
    payload: GastoTelegramCreate,
    session: AsyncSession = Depends(sesion_db),
    _: None = Depends(requiere_api_key),
) -> GastoTelegramRespuesta:
    service = GastoService(session)
    gasto, duplicado = await service.registrar_desde_telegram(payload)
    mensaje = (
        "El gasto ya estaba registrado (duplicado)"
        if duplicado
        else "Gasto registrado correctamente"
    )
    return GastoTelegramRespuesta(
        success=True,
        message=mensaje,
        duplicate=duplicado,
        data=GastoRead.model_validate(gasto),
    )


@router.get(
    "",
    response_model=GastoPaginadoRespuesta,
    summary="Listar gastos con filtros y paginacion",
)
async def listar_gastos(
    mes: int | None = Query(None, ge=1, le=12, description="Mes (1-12)"),
    anio: int | None = Query(None, ge=2000, le=2100, description="Anio"),
    fecha_desde: str | None = Query(None, description="Fecha inicial (ISO)"),
    fecha_hasta: str | None = Query(None, description="Fecha final (ISO)"),
    categoria_id: int | None = Query(None, gt=0),
    metodo_pago: str | None = Query(None),
    origen: str | None = Query(None, pattern="^(telegram|web)$"),
    q: str | None = Query(None, description="Busqueda por descripcion"),
    orden: OrdenGasto = Query("fecha_desc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=200),
    session: AsyncSession = Depends(sesion_db),
) -> GastoPaginadoRespuesta:
    service = GastoService(session)
    filtros = _filtros(
        service, mes, anio, fecha_desde, fecha_hasta, categoria_id, metodo_pago, origen, q
    )
    items, total = await service.listar(filtros, orden=orden, pagina=pagina, limite=limite)
    paginas = (total + limite - 1) // limite if limite else 0
    return GastoPaginadoRespuesta(
        success=True,
        message=f"{total} gasto(s) encontrado(s)",
        data=GastoPaginado(
            items=[GastoRead.model_validate(gasto) for gasto in items],
            total=total,
            pagina=pagina,
            limite=limite,
            paginas=paginas,
        ),
    )


@router.get(
    "/export/csv",
    summary="Exportar los gastos filtrados a CSV",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
async def exportar_gastos_csv(
    mes: int | None = Query(None, ge=1, le=12),
    anio: int | None = Query(None, ge=2000, le=2100),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    categoria_id: int | None = Query(None, gt=0),
    metodo_pago: str | None = Query(None),
    origen: str | None = Query(None, pattern="^(telegram|web)$"),
    q: str | None = Query(None),
    orden: OrdenGasto = Query("fecha_desc"),
    session: AsyncSession = Depends(sesion_db),
) -> Response:
    service = GastoService(session)
    filtros = _filtros(
        service, mes, anio, fecha_desde, fecha_hasta, categoria_id, metodo_pago, origen, q
    )
    gastos = await service.listar_todos(filtros, orden=orden)
    contenido = gastos_a_csv(gastos)
    return Response(
        content=contenido,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="gastos.csv"',
        },
    )


@router.get("/{gasto_id}", response_model=GastoOperacionRespuesta, summary="Obtener un gasto")
async def obtener_gasto(
    gasto_id: int,
    session: AsyncSession = Depends(sesion_db),
) -> GastoOperacionRespuesta:
    service = GastoService(session)
    gasto = await service.obtener(gasto_id)
    return GastoOperacionRespuesta(
        success=True,
        message="Gasto encontrado",
        data=GastoRead.model_validate(gasto),
    )


@router.post(
    "",
    response_model=GastoOperacionRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un gasto manual",
)
async def registrar_gasto(
    payload: GastoCreate,
    session: AsyncSession = Depends(sesion_db),
) -> GastoOperacionRespuesta:
    service = GastoService(session)
    gasto = await service.registrar_manual(payload)
    return GastoOperacionRespuesta(
        success=True,
        message="Gasto registrado correctamente",
        data=GastoRead.model_validate(gasto),
    )


@router.put(
    "/{gasto_id}",
    response_model=GastoOperacionRespuesta,
    summary="Modificar un gasto",
)
async def actualizar_gasto(
    gasto_id: int,
    payload: GastoUpdate,
    session: AsyncSession = Depends(sesion_db),
) -> GastoOperacionRespuesta:
    service = GastoService(session)
    gasto = await service.actualizar(gasto_id, payload)
    return GastoOperacionRespuesta(
        success=True,
        message="Gasto actualizado correctamente",
        data=GastoRead.model_validate(gasto),
    )


@router.delete(
    "/{gasto_id}",
    response_model=GastoOperacionRespuesta,
    summary="Eliminar un gasto",
)
async def eliminar_gasto(
    gasto_id: int,
    session: AsyncSession = Depends(sesion_db),
) -> GastoOperacionRespuesta:
    service = GastoService(session)
    gasto = await service.obtener(gasto_id)
    datos = GastoRead.model_validate(gasto)
    await service.eliminar(gasto_id)
    return GastoOperacionRespuesta(
        success=True,
        message="Gasto eliminado correctamente",
        data=datos,
    )
