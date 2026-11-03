from __future__ import annotations

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.timezone import days_in_month, default_zone, month_bounds_utc, previous_month
from app.repositories.gasto_repository import FiltrosGasto, GastoRepository
from app.schemas.dashboard import (
    CategoriaDistribucion,
    ComparacionMes,
    DashboardResumen,
    GastoPorDia,
)
from app.services.gasto_service import filtros_con_rango

CENTIMO = Decimal("0.01")


def _porcentaje(parte: Decimal, total: Decimal) -> float:
    if not total:
        return 0.0
    return float(((parte / total) * 100).quantize(CENTIMO, rounding=ROUND_HALF_UP))


class DashboardService:
    """Calcula las metricas del dashboard web."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.gastos_repo = GastoRepository(session)

    async def resumen(
        self,
        anio: int,
        mes: int,
        categoria_id: int | None = None,
        metodo_pago: str | None = None,
    ) -> DashboardResumen:
        zone = default_zone()
        inicio, fin = month_bounds_utc(anio, mes, zone)

        filtros_base = FiltrosGasto(categoria_id=categoria_id, metodo_pago=metodo_pago)
        filtros_mes = filtros_con_rango(filtros_base, inicio, fin)

        total, cantidad = await self.gastos_repo.totales(filtros_mes)
        promedio = (
            (total / cantidad).quantize(CENTIMO, rounding=ROUND_HALF_UP)
            if cantidad
            else Decimal("0.00")
        )

        distribucion = await self._distribucion(filtros_mes, total)
        gastos_por_dia = await self._gastos_por_dia(filtros_mes, anio, mes)
        comparacion = await self._comparacion(filtros_base, total, anio, mes)

        return DashboardResumen(
            anio=anio,
            mes=mes,
            moneda=get_settings().default_currency,
            total_gastado=total,
            cantidad_transacciones=cantidad,
            promedio_por_transaccion=promedio,
            categoria_mayor_gasto=distribucion[0] if distribucion else None,
            distribucion_por_categoria=distribucion,
            gastos_por_dia=gastos_por_dia,
            comparacion_mes_anterior=comparacion,
        )

    async def _distribucion(
        self,
        filtros: FiltrosGasto,
        total: Decimal,
    ) -> list[CategoriaDistribucion]:
        filas = await self.gastos_repo.por_categoria(filtros)
        return [
            CategoriaDistribucion(
                categoria_id=categoria_id,
                nombre=nombre,
                color=color,
                monto=monto,
                porcentaje=_porcentaje(monto, total),
            )
            for categoria_id, nombre, color, monto in filas
        ]

    async def _gastos_por_dia(
        self,
        filtros: FiltrosGasto,
        anio: int,
        mes: int,
    ) -> list[GastoPorDia]:
        timezone_name = get_settings().app_timezone
        filas = await self.gastos_repo.por_dia(filtros, timezone_name)
        por_dia: dict[str, Decimal] = {}
        for dia, monto in filas:
            if isinstance(dia, datetime):
                clave = dia.date().isoformat()
            elif isinstance(dia, date):
                clave = dia.isoformat()
            else:
                clave = str(dia)
            por_dia[clave] = monto

        resultado = []
        for numero in range(1, days_in_month(anio, mes) + 1):
            fecha = date(anio, mes, numero)
            resultado.append(
                GastoPorDia(
                    dia=numero,
                    fecha=fecha.isoformat(),
                    monto=por_dia.get(fecha.isoformat(), Decimal("0.00")),
                )
            )
        return resultado

    async def _comparacion(
        self,
        filtros_base: FiltrosGasto,
        total_actual: Decimal,
        anio: int,
        mes: int,
    ) -> ComparacionMes:
        zone = default_zone()
        anio_anterior, mes_anterior = previous_month(anio, mes)
        inicio, fin = month_bounds_utc(anio_anterior, mes_anterior, zone)
        total_anterior = await self.gastos_repo.totales_en_rango(filtros_base, inicio, fin)

        diferencia = (total_actual - total_anterior).quantize(CENTIMO, rounding=ROUND_HALF_UP)
        variacion = None
        if total_anterior:
            variacion = _porcentaje(diferencia, total_anterior)

        return ComparacionMes(
            total_actual=total_actual,
            total_anterior=total_anterior,
            diferencia=diferencia,
            variacion_porcentaje=variacion,
        )
