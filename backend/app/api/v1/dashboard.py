from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import sesion_db
from app.core.timezone import default_zone, today_local
from app.schemas.responses import DashboardRespuesta
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/resumen",
    response_model=DashboardRespuesta,
    summary="Resumen y estadisticas del dashboard",
    description=(
        "Calcula el total gastado, cantidad de transacciones, promedio, categoria "
        "con mayor gasto, distribucion por categoria, gastos por dia y comparacion "
        "con el mes anterior. Sin parametros devuelve el mes actual."
    ),
)
async def resumen_dashboard(
    anio: int | None = Query(None, ge=2000, le=2100),
    mes: int | None = Query(None, ge=1, le=12),
    categoria_id: int | None = Query(None, gt=0),
    metodo_pago: str | None = Query(None),
    session: AsyncSession = Depends(sesion_db),
) -> DashboardRespuesta:
    zone = default_zone()
    hoy: date = today_local(zone)
    anio_resuelto = anio or hoy.year
    mes_resuelto = mes or hoy.month

    service = DashboardService(session)
    resumen = await service.resumen(
        anio=anio_resuelto,
        mes=mes_resuelto,
        categoria_id=categoria_id,
        metodo_pago=metodo_pago,
    )
    return DashboardRespuesta(
        success=True,
        message=f"Resumen de {anio_resuelto}-{mes_resuelto:02d}",
        data=resumen,
    )
