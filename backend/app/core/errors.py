"""Manejo global de errores: todas las respuestas usan el envelope estandar."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Recurso inexistente (404)."""


class ConflictError(Exception):
    """Conflicto con el estado actual de los datos (409)."""


class ReglaNegocioError(Exception):
    """Operacion no permitida por las reglas de negocio (422)."""


def _envelope(success: bool, message: str, data: object | None = None) -> dict:
    payload: dict = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return payload


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "Error inesperado"
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(False, detail),
        headers=getattr(exc, "headers", None),
    )


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content=_envelope(False, str(exc)))


async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content=_envelope(False, str(exc)))


async def business_rule_handler(request: Request, exc: ReglaNegocioError) -> JSONResponse:
    return JSONResponse(status_code=422, content=_envelope(False, str(exc)))


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errores = []
    for error in exc.errors():
        ubicacion = " -> ".join(str(item) for item in error.get("loc", ())[1:]) or "body"
        errores.append(f"{ubicacion}: {error.get('msg', 'valor invalido')}")
    detalle = "; ".join(errores) or "Datos invalidos"
    return JSONResponse(
        status_code=422,
        content=_envelope(False, f"Datos invalidos: {detalle}", {"errores": errores}),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_envelope(False, "Error interno del servidor"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
    app.add_exception_handler(ReglaNegocioError, business_rule_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
