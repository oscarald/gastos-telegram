from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import MAX_DESCORIPCION, MAX_METODO_PAGO
from app.core.timezone import default_zone, to_local
from app.models.gasto import Gasto
from app.schemas.types import Monto, MontoPositivo


class GastoBase(BaseModel):
    monto: MontoPositivo
    descripcion: str = Field(min_length=1, max_length=MAX_DESCORIPCION)
    fecha: datetime | None = None
    metodo_pago: str | None = Field(default=None, max_length=MAX_METODO_PAGO)
    moneda: str = Field(default="BOB", min_length=3, max_length=3)

    @field_validator("descripcion")
    @classmethod
    def _normalizar_descripcion(cls, value: str) -> str:
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("La descripcion no puede estar vacia")
        return limpio

    @field_validator("metodo_pago")
    @classmethod
    def _normalizar_metodo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        limpio = " ".join(value.split())
        return limpio or None

    @field_validator("moneda")
    @classmethod
    def _validar_moneda(cls, value: str) -> str:
        return value.upper()

    @field_validator("fecha")
    @classmethod
    def _normalizar_fecha(cls, value: datetime | None) -> datetime | None:
        """Las fechas sin zona horaria se interpretan en la zona de la app."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=default_zone())
        return value


class GastoCreate(GastoBase):
    """Registro manual desde el dashboard web."""

    categoria_id: int | None = Field(default=None, gt=0)


class GastoTelegramCreate(GastoBase):
    """Registro originado en un mensaje de Telegram."""

    identificador_externo: str | None = Field(default=None, max_length=128)


class GastoUpdate(BaseModel):
    """Actualizacion parcial: solo se aplican los campos enviados."""

    monto: MontoPositivo | None = None
    descripcion: str | None = Field(default=None, min_length=1, max_length=MAX_DESCORIPCION)
    categoria_id: int | None = Field(default=None, gt=0)
    fecha: datetime | None = None
    metodo_pago: str | None = Field(default=None, max_length=MAX_METODO_PAGO)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("descripcion")
    @classmethod
    def _normalizar_descripcion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("La descripcion no puede estar vacia")
        return limpio

    @field_validator("moneda")
    @classmethod
    def _validar_moneda(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @field_validator("fecha")
    @classmethod
    def _normalizar_fecha(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=default_zone())
        return value


class GastoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    monto: Monto
    moneda: str
    descripcion: str
    categoria_id: int
    categoria: str
    categoria_color: str
    metodo_pago: str | None
    origen: str
    identificador_externo: str | None
    fecha: datetime
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _extraer_categoria(cls, data: Any) -> Any:
        if not isinstance(data, Gasto):
            return data
        categoria = data.categoria
        return {
            "id": data.id,
            "monto": data.monto,
            "moneda": data.moneda,
            "descripcion": data.descripcion,
            "categoria_id": data.categoria_id,
            "categoria": categoria.nombre if categoria else "Sin categoria",
            "categoria_color": categoria.color_hex if categoria else "#6B7280",
            "metodo_pago": data.metodo_pago,
            "origen": data.origen,
            "identificador_externo": data.identificador_externo,
            "fecha": to_local(data.fecha),
            "created_at": to_local(data.created_at),
            "updated_at": to_local(data.updated_at),
        }


class GastoPaginado(BaseModel):
    items: list[GastoRead]
    total: int
    pagina: int
    limite: int
    paginas: int
