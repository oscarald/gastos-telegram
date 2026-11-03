from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.regla import Regla
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.regla_repository import ReglaRepository
from app.schemas.regla import ReglaCreate, ReglaUpdate


class ReglaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reglas_repo = ReglaRepository(session)
        self.categorias_repo = CategoriaRepository(session)

    async def listar(self, solo_activas: bool = False) -> list[Regla]:
        return await self.reglas_repo.listar(solo_activas=solo_activas)

    async def obtener(self, regla_id: int) -> Regla:
        regla = await self.reglas_repo.get_by_id(regla_id)
        if regla is None:
            raise NotFoundError(f"No existe la regla con id {regla_id}")
        return regla

    async def _validar_categoria(self, categoria_id: int):
        categoria = await self.categorias_repo.get_by_id(categoria_id)
        if categoria is None:
            raise NotFoundError(f"No existe la categoria con id {categoria_id}")
        return categoria

    async def crear(self, payload: ReglaCreate) -> Regla:
        categoria = await self._validar_categoria(payload.categoria_id)
        duplicada = await self._buscar_duplicada(payload.palabra_clave, payload.categoria_id)
        if duplicada is not None:
            raise ConflictError(
                f"Ya existe la regla '{payload.palabra_clave}' para esa categoria"
            )
        regla = await self.reglas_repo.create(
            Regla(
                palabra_clave=payload.palabra_clave,
                categoria=categoria,
                prioridad=payload.prioridad,
                activa=payload.activa,
            )
        )
        await self.session.commit()
        return regla

    async def actualizar(self, regla_id: int, payload: ReglaUpdate) -> Regla:
        regla = await self.obtener(regla_id)
        datos = payload.model_dump(exclude_unset=True)

        palabra_clave = datos.get("palabra_clave", regla.palabra_clave)
        categoria_id = datos.get("categoria_id", regla.categoria_id)

        if "categoria_id" in datos and datos["categoria_id"] is not None:
            categoria = await self._validar_categoria(datos["categoria_id"])
            regla.categoria = categoria

        if palabra_clave != regla.palabra_clave or categoria_id != regla.categoria_id:
            duplicada = await self._buscar_duplicada(
                palabra_clave,
                categoria_id,
                excluir_id=regla.id,
            )
            if duplicada is not None:
                raise ConflictError(
                    f"Ya existe la regla '{palabra_clave}' para esa categoria"
                )

        if "palabra_clave" in datos and datos["palabra_clave"] is not None:
            regla.palabra_clave = datos["palabra_clave"]
        if "categoria_id" in datos and datos["categoria_id"] is not None:
            regla.categoria_id = datos["categoria_id"]
        if "prioridad" in datos and datos["prioridad"] is not None:
            regla.prioridad = datos["prioridad"]
        if "activa" in datos and datos["activa"] is not None:
            regla.activa = datos["activa"]

        await self.session.commit()
        return regla

    async def eliminar(self, regla_id: int) -> None:
        regla = await self.obtener(regla_id)
        await self.reglas_repo.delete(regla)
        await self.session.commit()

    async def _buscar_duplicada(
        self,
        palabra_clave: str,
        categoria_id: int,
        excluir_id: int | None = None,
    ) -> Regla | None:
        for regla in await self.reglas_repo.listar():
            if excluir_id is not None and regla.id == excluir_id:
                continue
            if (
                regla.palabra_clave.casefold() == palabra_clave.casefold()
                and regla.categoria_id == categoria_id
            ):
                return regla
        return None
