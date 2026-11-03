from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import MAX_PALABRA_CLAVE
from app.models.regla import Regla


class ReglaBase(BaseModel):
    palabra_clave: str = Field(min_length=1, max_length=MAX_PALABRA_CLAVE)
    categoria_id: int = Field(gt=0)
    prioridad: int = 0
    activa: bool = True

    @field_validator("palabra_clave")
    @classmethod
    def _normalizar_palabra(cls, value: str) -> str:
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("La palabra clave no puede estar vacia")
        return limpio.lower()


class ReglaCreate(ReglaBase):
    pass


class ReglaUpdate(BaseModel):
    palabra_clave: str | None = Field(default=None, min_length=1, max_length=MAX_PALABRA_CLAVE)
    categoria_id: int | None = Field(default=None, gt=0)
    prioridad: int | None = None
    activa: bool | None = None

    @field_validator("palabra_clave")
    @classmethod
    def _normalizar_palabra(cls, value: str | None) -> str | None:
        if value is None:
            return None
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("La palabra clave no puede estar vacia")
        return limpio.lower()


class ReglaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    palabra_clave: str
    categoria_id: int
    categoria: str
    categoria_color: str
    prioridad: int
    activa: bool
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _extraer_categoria(cls, data: Any) -> Any:
        if not isinstance(data, Regla):
            return data
        categoria = data.categoria
        return {
            "id": data.id,
            "palabra_clave": data.palabra_clave,
            "categoria_id": data.categoria_id,
            "categoria": categoria.nombre if categoria else "",
            "categoria_color": categoria.color_hex if categoria else "#6B7280",
            "prioridad": data.prioridad,
            "activa": data.activa,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
        }
