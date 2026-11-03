from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categoria import Categoria


class CategoriaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, categoria: Categoria) -> Categoria:
        self.session.add(categoria)
        await self.session.flush()
        return categoria

    async def get_by_id(self, categoria_id: int) -> Categoria | None:
        result = await self.session.execute(select(Categoria).where(Categoria.id == categoria_id))
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> Categoria | None:
        result = await self.session.execute(select(Categoria).where(Categoria.nombre == nombre))
        return result.scalar_one_or_none()

    async def listar(self, solo_activas: bool = False) -> list[Categoria]:
        consulta = select(Categoria)
        if solo_activas:
            consulta = consulta.where(Categoria.activa.is_(True))
        result = await self.session.execute(consulta.order_by(Categoria.nombre))
        return list(result.scalars().all())

    async def contar_gastos(self, categoria_id: int) -> int:
        from app.models.gasto import Gasto

        result = await self.session.execute(
            select(func.count(Gasto.id)).where(Gasto.categoria_id == categoria_id)
        )
        return int(result.scalar_one())

    async def contar_reglas(self, categoria_id: int) -> int:
        from app.models.regla import Regla

        result = await self.session.execute(
            select(func.count(Regla.id)).where(Regla.categoria_id == categoria_id)
        )
        return int(result.scalar_one())

    async def conteo_gastos_por_categoria(self) -> dict[int, int]:
        """Numero de gastos por categoria (una sola consulta)."""
        from app.models.gasto import Gasto

        result = await self.session.execute(
            select(Gasto.categoria_id, func.count(Gasto.id)).group_by(Gasto.categoria_id)
        )
        return {int(categoria_id): int(cantidad) for categoria_id, cantidad in result.all()}

    async def delete(self, categoria: Categoria) -> None:
        await self.session.delete(categoria)
        await self.session.flush()
