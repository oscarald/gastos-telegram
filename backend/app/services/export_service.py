from __future__ import annotations

import csv
import io

from app.core.timezone import to_local
from app.models.gasto import Gasto

CABECERA = [
    "Fecha",
    "Descripcion",
    "Categoria",
    "Metodo de pago",
    "Origen",
    "Monto",
    "Moneda",
    "Identificador externo",
]


def gastos_a_csv(gastos: list[Gasto]) -> bytes:
    """Serializa los gastos a CSV (UTF-8 con BOM para Excel)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
    writer.writerow(CABECERA)
    for gasto in gastos:
        categoria = gasto.categoria.nombre if gasto.categoria else ""
        writer.writerow(
            [
                to_local(gasto.fecha).strftime("%Y-%m-%d %H:%M"),
                gasto.descripcion,
                categoria,
                gasto.metodo_pago or "",
                gasto.origen,
                f"{gasto.monto:.2f}",
                gasto.moneda,
                gasto.identificador_externo or "",
            ]
        )
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")
