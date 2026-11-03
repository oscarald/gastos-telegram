from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.regla import Regla


class ReglaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, regla: Regla) -> Regla:
        self.session.add(regla)
        await self.session.flush()
        return regla

    async def get_by_id(self, regla_id: int) -> Regla | None:
        result = await self.session.execute(select(Regla).where(Regla.id == regla_id))
        return result.scalar_one_or_none()

    async def listar(self, solo_activas: bool = False) -> list[Regla]:
        consulta = select(Regla)
        if solo_activas:
            consulta = consulta.where(Regla.activa.is_(True))
        result = await self.session.execute(
            consulta.order_by(Regla.prioridad.desc(), Regla.palabra_clave)
        )
        return list(result.scalars().all())

    async def delete(self, regla: Regla) -> None:
        await self.session.delete(regla)
        await self.session.flush()
