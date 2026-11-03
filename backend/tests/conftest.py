"""Configuracion compartida de las pruebas.

Las pruebas unitarias no necesitan base de datos. Las de integracion usan
PostgreSQL real (para validar Numeric, TIMESTAMPTZ, indices y claves foraneas):

    docker compose -f docker-compose.test.yml up -d

La URL por defecto es postgresql+asyncpg://gastos:gastos@localhost:5433/gastos_test
(puedes sobrescribirla con la variable TEST_DATABASE_URL).
"""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://gastos:gastos@localhost:5433/gastos_test",
    ),
)
os.environ.setdefault("N8N_API_KEY", "clave-de-pruebas")
os.environ.setdefault("APP_TIMEZONE", "America/La_Paz")
os.environ.setdefault("DEFAULT_CURRENCY", "BOB")

from app.main import app  # noqa: E402,F401  (valida que la app importa correctamente)

API_KEY = "clave-de-pruebas"
URL_BASE = "http://testserver"
