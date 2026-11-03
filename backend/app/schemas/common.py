from typing import Any

from pydantic import BaseModel, ConfigDict


class MensajeRespuesta(BaseModel):
    """Envelope estandar de las respuestas de escritura."""

    success: bool = True
    message: str
    data: Any | None = None


class ErrorRespuesta(BaseModel):
    success: bool = False
    message: str
    data: dict[str, Any] | None = None


class HealthRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    app: str
    version: str
    database: str
    timezone: str
