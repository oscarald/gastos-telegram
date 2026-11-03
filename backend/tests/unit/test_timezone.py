"""Pruebas de las utilidades de zona horaria."""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app.core.timezone import (
    day_bounds_utc,
    days_in_month,
    month_bounds_utc,
    previous_month,
    to_local,
)

LA_PAZ = ZoneInfo("America/La_Paz")


class TestMonthBounds:
    def test_limites_de_mes_en_utc(self) -> None:
        inicio, fin = month_bounds_utc(2026, 11, LA_PAZ)
        assert inicio == datetime(2026, 11, 1, 4, 0, tzinfo=timezone.utc)
        assert fin == datetime(2026, 12, 1, 4, 0, tzinfo=timezone.utc)

    def test_diciembre_cruza_el_ano(self) -> None:
        inicio, fin = month_bounds_utc(2026, 12, LA_PAZ)
        assert inicio == datetime(2026, 12, 1, 4, 0, tzinfo=timezone.utc)
        assert fin == datetime(2027, 1, 1, 4, 0, tzinfo=timezone.utc)

    def test_enero(self) -> None:
        inicio, fin = month_bounds_utc(2026, 1, LA_PAZ)
        assert inicio == datetime(2026, 1, 1, 4, 0, tzinfo=timezone.utc)
        assert fin == datetime(2026, 2, 1, 4, 0, tzinfo=timezone.utc)


class TestDayBounds:
    def test_limites_de_dia(self) -> None:
        inicio, fin = day_bounds_utc(date(2026, 11, 2), LA_PAZ)
        assert inicio == datetime(2026, 11, 2, 4, 0, tzinfo=timezone.utc)
        assert fin == datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc)


class TestHelpers:
    def test_mes_anterior(self) -> None:
        assert previous_month(2026, 1) == (2025, 12)
        assert previous_month(2026, 11) == (2026, 10)

    def test_dias_del_mes(self) -> None:
        assert days_in_month(2026, 11) == 30
        assert days_in_month(2026, 2) == 28
        assert days_in_month(2024, 2) == 29
        assert days_in_month(2026, 12) == 31

    def test_to_local(self) -> None:
        utc = datetime(2026, 11, 2, 16, 30, tzinfo=timezone.utc)
        local = to_local(utc, LA_PAZ)
        assert local.hour == 12
        assert local.minute == 30
        assert local.utcoffset().total_seconds() == -4 * 3600
