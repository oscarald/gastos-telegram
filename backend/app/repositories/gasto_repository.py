from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gasto import Gasto


@dataclass(frozen=True)
class FiltrosGasto:
    """Filtros ya resueltos a UTC listos para consultar la base de datos."""

    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    categoria_id: int | None = None
    metodo_pago: str | None = None
    origen: str | None = None
    busqueda: str | None = None


class GastoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Consultas basicas
    # ------------------------------------------------------------------
    async def create(self, gasto: Gasto) -> Gasto:
        self.session.add(gasto)
        await self.session.flush()
        return gasto

    async def get_by_id(self, gasto_id: int) -> Gasto | None:
        result = await self.session.execute(select(Gasto).where(Gasto.id == gasto_id))
        return result.scalar_one_or_none()

    async def get_by_identificador_externo(self, identificador: str) -> Gasto | None:
        result = await self.session.execute(
            select(Gasto).where(Gasto.identificador_externo == identificador)
        )
        return result.scalar_one_or_none()

    async def delete(self, gasto: Gasto) -> None:
        await self.session.delete(gasto)
        await self.session.flush()

    # ------------------------------------------------------------------
    # Listado con filtros
    # ------------------------------------------------------------------
    def condiciones(self, filtros: FiltrosGasto) -> list:
        condiciones = []
        if filtros.fecha_desde is not None:
            condiciones.append(Gasto.fecha >= filtros.fecha_desde)
        if filtros.fecha_hasta is not None:
            condiciones.append(Gasto.fecha < filtros.fecha_hasta)
        if filtros.categoria_id is not None:
            condiciones.append(Gasto.categoria_id == filtros.categoria_id)
        if filtros.metodo_pago:
            condiciones.append(Gasto.metodo_pago == filtros.metodo_pago)
        if filtros.origen:
            condiciones.append(Gasto.origen == filtros.origen)
        if filtros.busqueda:
            condiciones.append(Gasto.descripcion.ilike(f"%{filtros.busqueda}%"))
        return condiciones

    async def listar(
        self,
        filtros: FiltrosGasto,
        orden: str = "fecha_desc",
        pagina: int = 1,
        limite: int = 20,
    ) -> tuple[list[Gasto], int]:
        condiciones = self.condiciones(filtros)

        total_result = await self.session.execute(
            select(func.count()).select_from(Gasto).where(*condiciones)
        )
        total = int(total_result.scalar_one())

        columnas = {
            "fecha_asc": Gasto.fecha.asc(),
            "fecha_desc": Gasto.fecha.desc(),
            "monto_asc": Gasto.monto.asc(),
            "monto_desc": Gasto.monto.desc(),
            "categoria_asc": Gasto.categoria_id.asc(),
        }
        orden_columna = columnas.get(orden, columnas["fecha_desc"])

        offset = max((pagina - 1) * limite, 0)
        consulta = (
            select(Gasto)
            .where(*condiciones)
            .order_by(orden_columna, Gasto.id.desc())
            .offset(offset)
            .limit(limite)
        )
        result = await self.session.execute(consulta)
        return list(result.scalars().all()), total

    async def listar_todos(self, filtros: FiltrosGasto, orden: str = "fecha_desc") -> list[Gasto]:
        """Listado sin paginacion (exportacion CSV)."""
        condiciones = self.condiciones(filtros)
        columnas = {
            "fecha_asc": Gasto.fecha.asc(),
            "fecha_desc": Gasto.fecha.desc(),
            "monto_asc": Gasto.monto.asc(),
            "monto_desc": Gasto.monto.desc(),
            "categoria_asc": Gasto.categoria_id.asc(),
        }
        orden_columna = columnas.get(orden, columnas["fecha_desc"])
        result = await self.session.execute(
            select(Gasto).where(*condiciones).order_by(orden_columna, Gasto.id.desc())
        )
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Agregaciones para el dashboard
    # ------------------------------------------------------------------
    async def totales(self, filtros: FiltrosGasto) -> tuple[Decimal, int]:
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(Gasto.monto), 0),
                func.count(Gasto.id),
            ).where(*self.condiciones(filtros))
        )
        total, cantidad = result.one()
        return total, int(cantidad)

    async def totales_en_rango(
        self,
        filtros: FiltrosGasto,
        fecha_desde: datetime,
        fecha_hasta: datetime,
    ) -> Decimal:
        condiciones = self.condiciones(filtros)
        condiciones.append(Gasto.fecha >= fecha_desde)
        condiciones.append(Gasto.fecha < fecha_hasta)
        result = await self.session.execute(
            select(func.coalesce(func.sum(Gasto.monto), 0)).where(*condiciones)
        )
        return result.scalar_one()

    async def por_categoria(self, filtros: FiltrosGasto) -> list[tuple[int, str, str, Decimal]]:
        from app.models.categoria import Categoria

        result = await self.session.execute(
            select(
                Categoria.id,
                Categoria.nombre,
                Categoria.color_hex,
                func.coalesce(func.sum(Gasto.monto), 0),
            )
            .join(Gasto, Gasto.categoria_id == Categoria.id)
            .where(*self.condiciones(filtros))
            .group_by(Categoria.id, Categoria.nombre, Categoria.color_hex)
            .order_by(func.sum(Gasto.monto).desc())
        )
        return [(int(row[0]), row[1], row[2], row[3]) for row in result.all()]

    async def por_dia(self, filtros: FiltrosGasto, timezone_name: str) -> list[tuple]:
        """Agrupacion por dia local (la columna fecha es TIMESTAMPTZ)."""
        dia_local = func.date(Gasto.fecha.op("AT TIME ZONE")(timezone_name))
        result = await self.session.execute(
            select(dia_local.label("dia"), func.coalesce(func.sum(Gasto.monto), 0).label("total"))
            .where(*self.condiciones(filtros))
            .group_by(dia_local)
            .order_by(dia_local)
        )
        return [(row[0], row[1]) for row in result.all()]
