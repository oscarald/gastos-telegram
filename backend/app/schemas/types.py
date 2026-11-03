"""Tipos de schema reutilizables."""

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, PlainSerializer


def _float_to_decimal(value: Any) -> Any:
    """Convierte floats a Decimal usando su representacion decimal exacta.

    Decimal(str(50.1)) == Decimal('50.1'), mientras que Decimal(50.1) arrastra
    el error binario de coma flotante.
    """
    if isinstance(value, float):
        return Decimal(str(value))
    return value


Monto = Annotated[
    Decimal,
    BeforeValidator(_float_to_decimal),
    PlainSerializer(lambda value: float(value), return_type=float, when_used="json"),
    Field(max_digits=12, decimal_places=2),
]

MontoPositivo = Annotated[
    Decimal,
    BeforeValidator(_float_to_decimal),
    PlainSerializer(lambda value: float(value), return_type=float, when_used="json"),
    Field(max_digits=12, decimal_places=2, gt=0),
]
