"""Pruebas de integracion de categorias y reglas."""

from __future__ import annotations

from httpx import AsyncClient

API = "/api/v1"


class TestCategorias:
    async def test_lista_las_categorias_iniciales(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/categorias")
        assert respuesta.status_code == 200
        nombres = {item["nombre"] for item in respuesta.json()["data"]}
        assert "Alimentación" in nombres
        assert "Sin Categorizar" in nombres
        assert len(respuesta.json()["data"]) == 7

    async def test_crea_categoria(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/categorias",
            json={
                "nombre": "Mascotas",
                "descripcion": "Alimento y veterinario",
                "color_hex": "#22C55E",
            },
        )
        assert respuesta.status_code == 201, respuesta.text
        data = respuesta.json()["data"]
        assert data["nombre"] == "Mascotas"
        assert data["color_hex"] == "#22C55E"
        assert data["activa"] is True

    async def test_no_permite_nombres_duplicados(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/categorias", json={"nombre": "Alimentación"}
        )
        assert respuesta.status_code == 409
        assert respuesta.json()["success"] is False

    async def test_rechaza_color_invalido(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/categorias", json={"nombre": "Mascotas", "color_hex": "verde"}
        )
        assert respuesta.status_code == 422

    async def test_actualiza_categoria(self, client: AsyncClient) -> None:
        listado = await client.get(f"{API}/categorias")
        objetivo = next(
            item for item in listado.json()["data"] if item["nombre"] == "Entretenimiento"
        )
        respuesta = await client.put(
            f"{API}/categorias/{objetivo['id']}",
            json={"nombre": "Ocio", "activa": False, "color_hex": "#EF4444"},
        )
        assert respuesta.status_code == 200
        data = respuesta.json()["data"]
        assert data["nombre"] == "Ocio"
        assert data["activa"] is False
        assert data["color_hex"] == "#EF4444"

    async def test_no_elimina_categoria_con_gastos(self, client: AsyncClient) -> None:
        gasto = await client.post(
            f"{API}/gastos",
            json={"monto": "10", "descripcion": "Almuerzo con regla"},
        )
        assert gasto.status_code == 201
        categorias = await client.get(f"{API}/categorias")
        alimentacion = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Alimentación"
        )

        respuesta = await client.delete(f"{API}/categorias/{alimentacion['id']}")
        assert respuesta.status_code == 409
        assert "gastos" in respuesta.json()["message"]

    async def test_elimina_reasignando_a_otra_categoria(self, client: AsyncClient) -> None:
        await client.post(
            f"{API}/gastos",
            json={"monto": "10", "descripcion": "Almuerzo con regla"},
        )
        categorias = await client.get(f"{API}/categorias")
        alimentacion = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Alimentación"
        )
        compras = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Compras"
        )

        respuesta = await client.delete(
            f"{API}/categorias/{alimentacion['id']}",
            params={"reemplazar_por": compras["id"]},
        )
        assert respuesta.status_code == 200

        listado = await client.get(f"{API}/gastos")
        assert listado.json()["data"]["items"][0]["categoria"] == "Compras"

    async def test_contador_de_gastos_por_categoria(self, client: AsyncClient) -> None:
        await client.post(
            f"{API}/gastos",
            json={"monto": "10", "descripcion": "Almuerzo con regla"},
        )
        categorias = await client.get(f"{API}/categorias")
        alimentacion = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Alimentación"
        )
        assert alimentacion["cantidad_gastos"] == 1


class TestReglas:
    async def test_lista_las_reglas_iniciales(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/reglas")
        assert respuesta.status_code == 200
        palabras = {item["palabra_clave"] for item in respuesta.json()["data"]}
        assert {"almuerzo", "desayuno", "supermercado", "pasaje"} <= palabras

    async def test_crea_regla(self, client: AsyncClient) -> None:
        categorias = await client.get(f"{API}/categorias")
        compras = next(item for item in categorias.json()["data"] if item["nombre"] == "Compras")

        respuesta = await client.post(
            f"{API}/reglas",
            json={"palabra_clave": "Zapatillas", "categoria_id": compras["id"], "prioridad": 5},
        )
        assert respuesta.status_code == 201, respuesta.text
        data = respuesta.json()["data"]
        assert data["palabra_clave"] == "zapatillas"
        assert data["categoria"] == "Compras"
        assert data["prioridad"] == 5

    async def test_no_permite_reglas_duplicadas(self, client: AsyncClient) -> None:
        categorias = await client.get(f"{API}/categorias")
        compras = next(item for item in categorias.json()["data"] if item["nombre"] == "Compras")

        primera = await client.post(
            f"{API}/reglas",
            json={"palabra_clave": "zapatillas", "categoria_id": compras["id"]},
        )
        assert primera.status_code == 201

        segunda = await client.post(
            f"{API}/reglas",
            json={"palabra_clave": "zapatillas", "categoria_id": compras["id"]},
        )
        assert segunda.status_code == 409

    async def test_actualiza_y_desactiva_regla(self, client: AsyncClient) -> None:
        reglas = await client.get(f"{API}/reglas")
        regla = next(item for item in reglas.json()["data"] if item["palabra_clave"] == "almuerzo")

        respuesta = await client.put(
            f"{API}/reglas/{regla['id']}", json={"prioridad": 99, "activa": False}
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["data"]["prioridad"] == 99
        assert respuesta.json()["data"]["activa"] is False

    async def test_regla_inactiva_no_categoriza(self, client: AsyncClient) -> None:
        reglas = await client.get(f"{API}/reglas")
        regla = next(item for item in reglas.json()["data"] if item["palabra_clave"] == "almuerzo")
        await client.put(f"{API}/reglas/{regla['id']}", json={"activa": False})

        gasto = await client.post(
            f"{API}/gastos", json={"monto": "10", "descripcion": "Almuerzo del dia"}
        )
        assert gasto.json()["data"]["categoria"] == "Sin Categorizar"

    async def test_elimina_regla(self, client: AsyncClient) -> None:
        reglas = await client.get(f"{API}/reglas")
        regla = next(item for item in reglas.json()["data"] if item["palabra_clave"] == "almuerzo")
        respuesta = await client.delete(f"{API}/reglas/{regla['id']}")
        assert respuesta.status_code == 200

        listado = await client.get(f"{API}/reglas")
        assert "almuerzo" not in {item["palabra_clave"] for item in listado.json()["data"]}

    async def test_categoria_inexistente(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/reglas", json={"palabra_clave": "prueba", "categoria_id": 9999}
        )
        assert respuesta.status_code == 404
