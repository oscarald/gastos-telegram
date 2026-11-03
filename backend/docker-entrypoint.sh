#!/bin/sh
set -e

echo "==> Aplicando migraciones (alembic upgrade head)"
alembic upgrade head

echo "==> Cargando datos iniciales (categorias y reglas)"
python -m app.db.seed

echo "==> Iniciando la API en 0.0.0.0:8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
