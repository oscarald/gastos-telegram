"""Autenticacion de la integracion con n8n.

La APIKey se valida en modo fail-closed: si no esta configurada en el entorno,
el endpoint protegido responde 503 en lugar de quedar abierto.
"""

import secrets

from fastapi import HTTPException, status

from app.core.config import get_settings


class ApiKeyInvalida(HTTPException):
    def __init__(self, detail: str = "API Key invalida o ausente") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def verify_api_key(provided_key: str | None) -> None:
    """Valida la cabecera X-API-Key contra el valor configurado."""
    expected_key = get_settings().n8n_api_key.strip()
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Integracion no disponible: N8N_API_KEY no esta configurada",
        )
    if not provided_key or not secrets.compare_digest(provided_key, expected_key):
        raise ApiKeyInvalida()
