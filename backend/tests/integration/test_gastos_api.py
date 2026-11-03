"""Pruebas de integracion de la API de gastos."""

from __future__ import annotations

from httpx import AsyncClient

API = "/api/v1"


async def _crear_telegram(
    client: AsyncClient,
    monto: str = "50.00",
    descripcion: str = "Almuerzo en restaurante",
    fecha: str | None = None,
    metodo_pago: str | None = "Efectivo",
    identificador: str | None = "telegram_123456",
) -> dict:
    cuerpo = {
        "monto": monto,
        "descripcion": descripcion,
        "fecha": fecha,
        "metodo_pago": metodo_pago,
        "identificador_externo": identificador,
    }
    respuesta = await client.post(
        f"{API}/gastos/telegram",
        json=cuerpo,
        headers={"X-API-Key": "clave-de-pruebas"},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


class TestRegistroTelegram:
    async def test_requiere_api_key(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos/telegram",
            json={"monto": 10, "descripcion": "Almuerzo"},
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["success"] is False

    async def test_rechaza_api_key_incorrecta(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos/telegram",
            json={"monto": 10, "descripcion": "Almuerzo"},
            headers={"X-API-Key": "incorrecta"},
        )
        assert respuesta.status_code == 401

    async def test_registra_y_categoriza_automaticamente(self, client: AsyncClient) -> None:
        cuerpo = await _crear_telegram(client)
        assert cuerpo["success"] is True
        assert cuerpo["duplicate"] is False
        assert cuerpo["message"] == "Gasto registrado correctamente"

        data = cuerpo["data"]
        assert data["id"] > 0
        assert data["monto"] == 50.0
        assert data["moneda"] == "BOB"
        assert data["descripcion"] == "Almuerzo en restaurante"
        assert data["categoria"] == "Alimentación"
        assert data["metodo_pago"] == "Efectivo"
        assert data["origen"] == "telegram"
        assert data["identificador_externo"] == "telegram_123456"

    async def test_evita_duplicados(self, client: AsyncClient) -> None:
        primero = await _crear_telegram(client)
        segundo = await _crear_telegram(client, monto="99.00")

        assert segundo["duplicate"] is True
        assert segundo["data"]["id"] == primero["data"]["id"]
        assert segundo["data"]["monto"] == 50.0

        listado = await client.get(f"{API}/gastos")
        assert listado.json()["data"]["total"] == 1

    async def test_sin_identificador_externo_no_hay_deduplicacion(
        self,
        client: AsyncClient,
    ) -> None:
        await _crear_telegram(client, identificador=None)
        await _crear_telegram(client, identificador=None)
        listado = await client.get(f"{API}/gastos")
        assert listado.json()["data"]["total"] == 2

    async def test_rechaza_monto_cero(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos/telegram",
            json={"monto": 0, "descripcion": "Almuerzo"},
            headers={"X-API-Key": "clave-de-pruebas"},
        )
        assert respuesta.status_code == 422
        assert respuesta.json()["success"] is False

    async def test_rechaza_monto_negativo(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos/telegram",
            json={"monto": -25, "descripcion": "Almuerzo"},
            headers={"X-API-Key": "clave-de-pruebas"},
        )
        assert respuesta.status_code == 422

    async def test_rechaza_descripcion_vacia(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos/telegram",
            json={"monto": 25, "descripcion": ""},
            headers={"X-API-Key": "clave-de-pruebas"},
        )
        assert respuesta.status_code == 422

    async def test_usa_fecha_enviada(self, client: AsyncClient) -> None:
        cuerpo = await _crear_telegram(
            client,
            fecha="2026-10-05T12:30:00-04:00",
            identificador="telegram_fecha",
        )
        assert cuerpo["data"]["fecha"].startswith("2026-10-05T12:30:00-04:00")


class TestRegistroManual:
    async def test_registra_gasto_web(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos",
            json={"monto": "120.50", "descripcion": "Compra de ropa"},
        )
        assert respuesta.status_code == 201, respuesta.text
        data = respuesta.json()["data"]
        assert data["origen"] == "web"
        assert data["monto"] == 120.5
        assert data["categoria"] == "Sin Categorizar"

    async def test_asigna_categoria_por_defecto(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos",
            json={"monto": "30", "descripcion": "Pasaje en micros"},
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["data"]["categoria"] == "Transporte"

    async def test_acepta_categoria_explicita(self, client: AsyncClient) -> None:
        categorias = await client.get(f"{API}/categorias")
        compras = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Compras"
        )
        respuesta = await client.post(
            f"{API}/gastos",
            json={
                "monto": "30",
                "descripcion": "Zapatillas",
                "categoria_id": compras["id"],
            },
        )
        assert respuesta.status_code == 201
        assert respuesta.json()["data"]["categoria"] == "Compras"

    async def test_categoria_inexistente(self, client: AsyncClient) -> None:
        respuesta = await client.post(
            f"{API}/gastos",
            json={"monto": "30", "descripcion": "Zapatillas", "categoria_id": 9999},
        )
        assert respuesta.status_code == 404


class TestConsultaEdicionEliminacion:
    async def test_obtener_gasto(self, client: AsyncClient) -> None:
        creado = await _crear_telegram(client)
        gasto_id = creado["data"]["id"]
        respuesta = await client.get(f"{API}/gastos/{gasto_id}")
        assert respuesta.status_code == 200
        assert respuesta.json()["data"]["id"] == gasto_id

    async def test_obtener_gasto_inexistente(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/gastos/9999")
        assert respuesta.status_code == 404

    async def test_actualiza_gasto(self, client: AsyncClient) -> None:
        creado = await _crear_telegram(client)
        gasto_id = creado["data"]["id"]

        respuesta = await client.put(
            f"{API}/gastos/{gasto_id}",
            json={"monto": "75.25", "descripcion": "Cena con amigos"},
        )
        assert respuesta.status_code == 200, respuesta.text
        data = respuesta.json()["data"]
        assert data["monto"] == 75.25
        assert data["descripcion"] == "Cena con amigos"
        assert data["categoria"] == "Sin Categorizar"

    async def test_actualiza_categoria_explicita(self, client: AsyncClient) -> None:
        creado = await _crear_telegram(client)
        categorias = await client.get(f"{API}/categorias")
        salud = next(item for item in categorias.json()["data"] if item["nombre"] == "Salud")

        respuesta = await client.put(
            f"{API}/gastos/{creado['data']['id']}",
            json={"categoria_id": salud["id"]},
        )
        assert respuesta.status_code == 200
        assert respuesta.json()["data"]["categoria"] == "Salud"

    async def test_elimina_gasto(self, client: AsyncClient) -> None:
        creado = await _crear_telegram(client)
        gasto_id = creado["data"]["id"]

        respuesta = await client.delete(f"{API}/gastos/{gasto_id}")
        assert respuesta.status_code == 200

        consulta = await client.get(f"{API}/gastos/{gasto_id}")
        assert consulta.status_code == 404

        listado = await client.get(f"{API}/gastos")
        assert listado.json()["data"]["total"] == 0


class TestFiltros:
    async def _crear_varios(self, client: AsyncClient) -> None:
        await _crear_telegram(
            client,
            monto="10",
            descripcion="Almuerzo de octubre",
            fecha="2026-10-05T12:00:00-04:00",
            metodo_pago="Efectivo",
            identificador="oct-1",
        )
        await _crear_telegram(
            client,
            monto="20",
            descripcion="Supermercado de octubre",
            fecha="2026-10-20T12:00:00-04:00",
            metodo_pago="Tarjeta de crédito",
            identificador="oct-2",
        )
        await _crear_telegram(
            client,
            monto="30",
            descripcion="Gasolina de noviembre",
            fecha="2026-11-02T12:00:00-04:00",
            metodo_pago="Efectivo",
            identificador="nov-1",
        )

    async def test_filtro_por_mes_y_anio(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(f"{API}/gastos", params={"mes": 10, "anio": 2026})
        datos = respuesta.json()["data"]
        assert datos["total"] == 2
        assert all(gasto["fecha"].startswith("2026-10") for gasto in datos["items"])

    async def test_filtro_por_rango_de_fechas(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(
            f"{API}/gastos",
            params={"fecha_desde": "2026-10-01", "fecha_hasta": "2026-10-31"},
        )
        assert respuesta.json()["data"]["total"] == 2

    async def test_filtro_por_categoria(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        categorias = await client.get(f"{API}/categorias")
        alimentacion = next(
            item for item in categorias.json()["data"] if item["nombre"] == "Alimentación"
        )
        respuesta = await client.get(
            f"{API}/gastos", params={"categoria_id": alimentacion["id"]}
        )
        assert respuesta.json()["data"]["total"] == 2

    async def test_filtro_por_metodo_de_pago(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(
            f"{API}/gastos", params={"metodo_pago": "Efectivo"}
        )
        assert respuesta.json()["data"]["total"] == 2

    async def test_busqueda_por_descripcion(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(f"{API}/gastos", params={"q": "gasolina"})
        datos = respuesta.json()["data"]
        assert datos["total"] == 1
        assert datos["items"][0]["descripcion"] == "Gasolina de noviembre"

    async def test_orden_por_monto(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(f"{API}/gastos", params={"orden": "monto_asc"})
        montos = [gasto["monto"] for gasto in respuesta.json()["data"]["items"]]
        assert montos == sorted(montos)

    async def test_paginacion(self, client: AsyncClient) -> None:
        await self._crear_varios(client)
        respuesta = await client.get(
            f"{API}/gastos", params={"pagina": 1, "limite": 2}
        )
        datos = respuesta.json()["data"]
        assert datos["total"] == 3
        assert datos["paginas"] == 2
        assert len(datos["items"]) == 2

    async def test_mes_sin_anio_es_error(self, client: AsyncClient) -> None:
        respuesta = await client.get(f"{API}/gastos", params={"mes": 10})
        assert respuesta.status_code == 422


class TestExportacion:
    async def test_exporta_csv_respetando_filtros(self, client: AsyncClient) -> None:
        await _crear_telegram(
            client,
            monto="10",
            descripcion="Almuerzo exportado",
            fecha="2026-10-05T12:00:00-04:00",
            identificador="exp-1",
        )
        await _crear_telegram(
            client,
            monto="20",
            descripcion="Gasto de noviembre",
            fecha="2026-11-05T12:00:00-04:00",
            identificador="exp-2",
        )

        respuesta = await client.get(
            f"{API}/gastos/export/csv", params={"mes": 10, "anio": 2026}
        )
        assert respuesta.status_code == 200
        assert "text/csv" in respuesta.headers["content-type"]
        assert "attachment" in respuesta.headers["content-disposition"]

        contenido = respuesta.content.decode("utf-8")
        assert contenido.startswith("\ufeff")
        assert "Almuerzo exportado" in contenido
        assert "Gasto de noviembre" not in contenido
