from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.categorias import router as categorias_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.gastos import router as gastos_router
from app.api.v1.reglas import router as reglas_router
from app.api.v1.salud import router as salud_router
from app.core.constants import METODOS_PAGO
from app.schemas.responses import MetodosPagoRespuesta

api_router = APIRouter()
api_router.include_router(salud_router)
api_router.include_router(gastos_router)
api_router.include_router(categorias_router)
api_router.include_router(reglas_router)
api_router.include_router(dashboard_router)


@api_router.get(
    "/metodos-pago",
    response_model=MetodosPagoRespuesta,
    tags=["Sistema"],
    summary="Metodos de pago disponibles",
)
async def metodos_pago() -> MetodosPagoRespuesta:
    return MetodosPagoRespuesta(
        success=True,
        message="Metodos de pago configurados",
        data=METODOS_PAGO,
    )
