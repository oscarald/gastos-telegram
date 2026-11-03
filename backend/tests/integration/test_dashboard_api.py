"""Pruebas de integracion del dashboard y de los seeds."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed

API = "/api/v1"


async def _crear_gasto(
    client: AsyncClient,
    monto: str,
    descripcion: str,
    fecha: str,
    metodo_pago: str = "Efectivo",
) -> None:
    respuesta = await client.post(
        f"{API}/gastos",
        json={
            "monto": monto,
            "descripcion": descripcion,
            "fecha": fecha,
            "metodo_pago": metodo_pago,
        },
    )
    assert respuesta.status_code == 201, respuesta.text


class TestDashboard:
    async def test_resumen_vacio(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/dashboard/resumen", params={"anio": 2026, "mes": 11})
        assert respuesta.status_code == 200
        data = respuesta.json()["data"]
        assert data["total_gastado"] == 0
        assert data["cantidad_transacciones"] == 0
        assert data["promedio_por_transaccion"] == 0
        assert data["categoria_mayor_gasto"] is None
        assert data["distribucion_por_categoria"] == []
        assert len(data["gastos_por_dia"]) == 30

    async def test_resumen_con_gastos(self, client: AsyncClient) -> None:
        await _crear_gasto(client, "100.00", "Almuerzo", "2026-11-02T12:00:00-04:00")
        await _crear_gasto(client, "50.50", "Pasaje", "2026-11-02T18:00:00-04:00")
        await _crear_gasto(client, "24.50", "Cafe", "2026-11-03T09:00:00-04:00")
        await _crear_gasto(client, "1000.00", "Compra", "2026-10-10T09:00:00-04:00")

        respuesta = await client.get(f"{API}/dashboard/resumen", params={"anio": 2026, "mes": 11})
        data = respuesta.json()["data"]

        assert data["total_gastado"] == 175.0
        assert data["cantidad_transacciones"] == 3
        assert data["promedio_por_transaccion"] == 58.33
        assert data["categoria_mayor_gasto"]["nombre"] == "Alimentación"
        assert data["categoria_mayor_gasto"]["monto"] == 100.0

        distribucion = {item["nombre"]: item for item in data["distribucion_por_categoria"]}
        assert set(distribucion) == {"Alimentación", "Transporte", "Sin Categorizar"}
        assert distribucion["Alimentación"]["monto"] == 100.0
        assert distribucion["Alimentación"]["porcentaje"] == 57.14
        assert distribucion["Transporte"]["porcentaje"] == 28.86

        dia_2 = next(item for item in data["gastos_por_dia"] if item["dia"] == 2)
        dia_3 = next(item for item in data["gastos_por_dia"] if item["dia"] == 3)
        dia_4 = next(item for item in data["gastos_por_dia"] if item["dia"] == 4)
        assert dia_2["monto"] == 150.5
        assert dia_3["monto"] == 24.5
        assert dia_4["monto"] == 0

    async def test_comparacion_con_mes_anterior(self, client: AsyncClient) -> None:
        await _crear_gasto(client, "100.00", "Almuerzo", "2026-11-02T12:00:00-04:00")
        await _crear_gasto(client, "50.00", "Almuerzo", "2026-10-02T12:00:00-04:00")

        respuesta = await client.get(f"{API}/dashboard/resumen", params={"anio": 2026, "mes": 11})
        comparacion = respuesta.json()["data"]["comparacion_mes_anterior"]
        assert comparacion["total_actual"] == 100.0
        assert comparacion["total_anterior"] == 50.0
        assert comparacion["diferencia"] == 50.0
        assert comparacion["variacion_porcentaje"] == 100.0

    async def test_usa_el_mes_actual_por_defecto(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/dashboard/resumen")
        assert respuesta.status_code == 200
        data = respuesta.json()["data"]
        assert data["anio"] >= 2026
        assert 1 <= data["mes"] <= 12

    async def test_filtra_por_categoria(self, client: AsyncClient) -> None:
        await _crear_gasto(client, "100.00", "Almuerzo", "2026-11-02T12:00:00-04:00")
        await _crear_gasto(client, "50.00", "Cafe", "2026-11-03T12:00:00-04:00")

        categorias = await client.get(f"{API}/categorias")
        alimentacion = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Alimentación"
        )
        respuesta = await client.get(
            f"{API}/dashboard/resumen",
            params={"anio": 2026, "mes": 11, "categoria_id": alimentacion["id"]},
        )
        data = respuesta.json()["data"]
        assert data["total_gastado"] == 100.0
        assert data["cantidad_transacciones"] == 1


class TestHealth:
    async def test_health(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/health")
        assert respuesta.status_code == 200
        assert respuesta.json()["status"] == "ok"
        assert respuesta.json()["database"] == "ok"


class TestMetodosPago:
    async def test_lista_metodos(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/metodos-pago")
        assert respuesta.status_code == 200
        assert "Efectivo" in respuesta.json()["data"]


class TestSeeds:
    async def test_seed_es_idempotente(self, db_session: AsyncSession) -> None:
        await seed(db_session)
        await seed(db_session)

        from sqlalchemy import func, select

        from app.models.categoria import Categoria
        from app.models.regla import Regla

        categorias = await db_session.execute(select(func.count(Categoria.id)))
        reglas = await db_session.execute(select(func.count(Regla.id)))

        assert categorias.scalar_one() == 7
        assert reglas.scalar_one() == 7
