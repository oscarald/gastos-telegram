"""Pruebas de validacion de montos y fechas de los esquemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.gasto import GastoCreate, GastoTelegramCreate


class TestMonto:
    def test_acepta_decimal_de_dos_cifras(self) -> None:
        payload = GastoCreate(monto="50.10", descripcion="Almuerzo")
        assert payload.monto == Decimal("50.10")

    def test_convierte_float_sin_ruido_binario(self) -> None:
        payload = GastoCreate(monto=50.10, descripcion="Almuerzo")
        assert payload.monto == Decimal("50.1")

    @pytest.mark.parametrize("valor", [0, -1, -0.01])
    def test_rechaza_montos_no_positivos(self, valor: float) -> None:
        with pytest.raises(ValidationError):
            GastoCreate(monto=valor, descripcion="Almuerzo")

    def test_rechaza_mas_de_dos_decimales(self) -> None:
        with pytest.raises(ValidationError):
            GastoCreate(monto="50.005", descripcion="Almuerzo")

    def test_rechaza_montos_absurdos(self) -> None:
        with pytest.raises(ValidationError):
            GastoCreate(monto="1234567890123.00", descripcion="Almuerzo")

    def test_serializa_como_numero_json(self) -> None:
        payload = GastoCreate(monto="50.10", descripcion="Almuerzo")
        assert payload.model_dump(mode="json")["monto"] == 50.1


class TestDescripcion:
    def test_normaliza_espacios(self) -> None:
        payload = GastoCreate(monto="10", descripcion="  Almuerzo   en casa ")
        assert payload.descripcion == "Almuerzo en casa"

    def test_rechaza_descripcion_vacia(self) -> None:
        with pytest.raises(ValidationError):
            GastoCreate(monto="10", descripcion="   ")

    def test_rechaza_descripcion_larga(self) -> None:
        with pytest.raises(ValidationError):
            GastoCreate(monto="10", descripcion="x" * 256)


class TestTelegram:
    def test_acepta_identificador_externo(self) -> None:
        payload = GastoTelegramCreate(
            monto="25",
            descripcion="Cafe",
            identificador_externo="telegram_123",
        )
        assert payload.identificador_externo == "telegram_123"

    def test_fecha_opcional(self) -> None:
        payload = GastoTelegramCreate(monto="25", descripcion="Cafe")
        assert payload.fecha is None

    def test_fecha_con_zona_horaria(self) -> None:
        payload = GastoTelegramCreate(
            monto="25",
            descripcion="Cafe",
            fecha=datetime.fromisoformat("2026-11-02T12:30:00-04:00"),
        )
        assert payload.fecha is not None
        assert payload.fecha.utcoffset().total_seconds() == -4 * 3600
