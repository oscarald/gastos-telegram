from pydantic import BaseModel, Field

from app.schemas.types import Monto


class CategoriaDistribucion(BaseModel):
    categoria_id: int
    nombre: str
    color: str
    monto: Monto
    porcentaje: float


class GastoPorDia(BaseModel):
    dia: int
    fecha: str
    monto: Monto


class ComparacionMes(BaseModel):
    total_actual: Monto
    total_anterior: Monto
    diferencia: Monto
    variacion_porcentaje: float | None


class DashboardResumen(BaseModel):
    anio: int
    mes: int
    moneda: str = "BOB"
    total_gastado: Monto
    cantidad_transacciones: int
    promedio_por_transaccion: Monto
    categoria_mayor_gasto: CategoriaDistribucion | None = None
    distribucion_por_categoria: list[CategoriaDistribucion] = Field(default_factory=list)
    gastos_por_dia: list[GastoPorDia] = Field(default_factory=list)
    comparacion_mes_anterior: ComparacionMes
