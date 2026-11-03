from pydantic import BaseModel

from app.schemas.categoria import CategoriaRead
from app.schemas.dashboard import DashboardResumen
from app.schemas.gasto import GastoPaginado, GastoRead
from app.schemas.regla import ReglaRead


class GastoOperacionRespuesta(BaseModel):
    success: bool = True
    message: str
    data: GastoRead


class GastoTelegramRespuesta(BaseModel):
    success: bool = True
    message: str
    duplicate: bool = False
    data: GastoRead


class GastoPaginadoRespuesta(BaseModel):
    success: bool = True
    message: str
    data: GastoPaginado


class CategoriaOperacionRespuesta(BaseModel):
    success: bool = True
    message: str
    data: CategoriaRead


class CategoriaListaRespuesta(BaseModel):
    success: bool = True
    message: str
    data: list[CategoriaRead]


class ReglaOperacionRespuesta(BaseModel):
    success: bool = True
    message: str
    data: ReglaRead


class ReglaListaRespuesta(BaseModel):
    success: bool = True
    message: str
    data: list[ReglaRead]


class DashboardRespuesta(BaseModel):
    success: bool = True
    message: str
    data: DashboardResumen


class MetodosPagoRespuesta(BaseModel):
    success: bool = True
    message: str
    data: list[str]
