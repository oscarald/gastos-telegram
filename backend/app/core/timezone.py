"""Utilidades de zona horaria.

La application's zona horaria de referencia es America/La_Paz, pero es configurable.
Los limites de mes/dia se calculan en hora local y se convierten a UTC para
consultar la base de datos (las columnas se guardan como TIMESTAMPTZ).
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.config import get_settings


def default_zone() -> ZoneInfo:
    """Zona horaria configurada en la aplicacion."""
    name = get_settings().app_timezone
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:  # pragma: no cover - configuracion invalida
        raise ValueError(f"Zona horaria invalida: {name}") from exc


def local_now(zone: ZoneInfo | None = None) -> datetime:
    """Instante actual en la zona horaria de la aplicacion."""
    zone = zone or default_zone()
    return datetime.now(zone)


def local_now_utc() -> datetime:
    """Instante actual en UTC (para persistir)."""
    return datetime.now(timezone.utc)


def today_local(zone: ZoneInfo | None = None) -> date:
    zone = zone or default_zone()
    return datetime.now(zone).date()


def to_local(value: datetime, zone: ZoneInfo | None = None) -> datetime:
    """Convierte a la zona horaria de la aplicacion."""
    zone = zone or default_zone()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(zone)


def month_bounds_utc(
    year: int,
    month: int,
    zone: ZoneInfo | None = None,
) -> tuple[datetime, datetime]:
    """Limites [inicio, fin) del mes local en UTC.

    El fin es exclusivo: se usa como comparacion `fecha < fin`.
    """
    zone = zone or default_zone()
    start_local = datetime(year, month, 1, tzinfo=zone)
    if month == 12:
        end_local = datetime(year + 1, 1, 1, tzinfo=zone)
    else:
        end_local = datetime(year, month + 1, 1, tzinfo=zone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def day_bounds_utc(day: date, zone: ZoneInfo | None = None) -> tuple[datetime, datetime]:
    """Limites [inicio, fin) del dia local en UTC."""
    zone = zone or default_zone()
    start_local = datetime(day.year, day.month, day.day, tzinfo=zone)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def previous_month(year: int, month: int) -> tuple[int, int]:
    """Devuelve (anio, mes) del mes anterior al indicado."""
    if month == 1:
        return year - 1, 12
    return year, month - 1


def days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - date(year, month, 1)).days
