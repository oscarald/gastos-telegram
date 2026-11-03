from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import COLOR_HEX_PATTERN, MAX_NOMBRE_CATEGORIA


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=MAX_NOMBRE_CATEGORIA)
    descripcion: str | None = Field(default=None, max_length=255)
    color_hex: str = Field(default="#6B7280", pattern=COLOR_HEX_PATTERN)
    activa: bool = True

    @field_validator("nombre")
    @classmethod
    def _normalizar_nombre(cls, value: str) -> str:
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("El nombre no puede estar vacio")
        return limpio


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=MAX_NOMBRE_CATEGORIA)
    descripcion: str | None = Field(default=None, max_length=255)
    color_hex: str | None = Field(default=None, pattern=COLOR_HEX_PATTERN)
    activa: bool | None = None

    @field_validator("nombre")
    @classmethod
    def _normalizar_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return None
        limpio = " ".join(value.split())
        if not limpio:
            raise ValueError("El nombre no puede estar vacio")
        return limpio


class CategoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    color_hex: str
    activa: bool
    cantidad_gastos: int = 0
    created_at: datetime
    updated_at: datetime
