from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, ReglaNegocioError
from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaRead, CategoriaUpdate


class CategoriaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.categorias_repo = CategoriaRepository(session)

    async def listar(self, solo_activas: bool = False) -> list[Categoria]:
        return await self.categorias_repo.listar(solo_activas=solo_activas)

    async def listar_con_conteo(self, solo_activas: bool = False) -> list[CategoriaRead]:
        """Categorias con la cantidad de gastos asociados."""
        categorias = await self.categorias_repo.listar(solo_activas=solo_activas)
        conteo = await self.categorias_repo.conteo_gastos_por_categoria()
        resultado = []
        for categoria in categorias:
            schema = CategoriaRead.model_validate(categoria)
            schema.cantidad_gastos = conteo.get(categoria.id, 0)
            resultado.append(schema)
        return resultado


    async def obtener(self, categoria_id: int) -> Categoria:
        categoria = await self.categorias_repo.get_by_id(categoria_id)
        if categoria is None:
            raise NotFoundError(f"No existe la categoria con id {categoria_id}")
        return categoria

    async def crear(self, payload: CategoriaCreate) -> Categoria:
        existente = await self.categorias_repo.get_by_nombre(payload.nombre)
        if existente is not None:
            raise ConflictError(f"Ya existe una categoria llamada '{payload.nombre}'")
        categoria = await self.categorias_repo.create(
            Categoria(
                nombre=payload.nombre,
                descripcion=payload.descripcion,
                color_hex=payload.color_hex.upper(),
                activa=payload.activa,
            )
        )
        await self.session.commit()
        return categoria

    async def actualizar(self, categoria_id: int, payload: CategoriaUpdate) -> Categoria:
        categoria = await self.obtener(categoria_id)
        datos = payload.model_dump(exclude_unset=True)

        if "nombre" in datos and datos["nombre"] is not None:
            nombre = datos["nombre"]
            if nombre != categoria.nombre:
                existente = await self.categorias_repo.get_by_nombre(nombre)
                if existente is not None:
                    raise ConflictError(f"Ya existe una categoria llamada '{nombre}'")
            categoria.nombre = nombre
        if "descripcion" in datos:
            categoria.descripcion = datos["descripcion"]
        if "color_hex" in datos and datos["color_hex"] is not None:
            categoria.color_hex = datos["color_hex"].upper()
        if "activa" in datos and datos["activa"] is not None:
            categoria.activa = datos["activa"]

        await self.session.commit()
        return categoria

    async def eliminar(self, categoria_id: int, reemplazar_por: int | None = None) -> None:
        """Elimina una categoria.

        Si tiene gastos o reglas asociados se exige una categoria destino
        (`reemplazar_por`) para no perder informacion historica.
        """
        categoria = await self.obtener(categoria_id)
        gastos = await self.categorias_repo.contar_gastos(categoria_id)
        reglas = await self.categorias_repo.contar_reglas(categoria_id)

        if (gastos or reglas) and reemplazar_por is None:
            raise ConflictError(
                f"La categoria '{categoria.nombre}' tiene {gastos} gastos y {reglas} reglas "
                "asociadas. Reasignalos con el parametro reemplazar_por antes de eliminarla."
            )

        if reemplazar_por is not None:
            destino = await self.obtener(reemplazar_por)
            if destino.id == categoria.id:
                raise ReglaNegocioError("La categoria destino debe ser distinta")
            await self._reasignar(categoria, destino)

        await self.categorias_repo.delete(categoria)
        await self.session.commit()

    async def _reasignar(self, origen: Categoria, destino: Categoria) -> None:
        """Mueve gastos y reglas a la categoria destino.

        Se actualizan objetos ORM (y no con UPDATE masivo) para mantener
        consistente el estado de la sesion y disparar `updated_at`.
        """
        from sqlalchemy import select

        from app.models.gasto import Gasto
        from app.models.regla import Regla

        gastos = (
            await self.session.execute(select(Gasto).where(Gasto.categoria_id == origen.id))
        ).scalars().all()
        for gasto in gastos:
            gasto.categoria = destino

        reglas = (
            await self.session.execute(select(Regla).where(Regla.categoria_id == origen.id))
        ).scalars().all()
        for regla in reglas:
            regla.categoria = destino

        await self.session.flush()

    async def cantidad_gastos(self, categoria_id: int) -> int:
        return await self.categorias_repo.contar_gastos(categoria_id)
