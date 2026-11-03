"""Carga idempotente de datos iniciales (categorias y reglas por defecto)."""

from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CATEGORIA_SIN_CATEGORIZAR, COLOR_SIN_CATEGORIZAR
from app.db.session import AsyncSessionLocal, dispose_engine
from app.models.categoria import Categoria
from app.models.regla import Regla
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.regla_repository import ReglaRepository

CATEGORIAS_INICIALES: list[tuple[str, str, str]] = [
    ("Alimentación", "#F59E0B", "Comidas, mercado y despensa"),
    ("Transporte", "#3B82F6", "Pasajes, gasolina y transporte público"),
    ("Servicios", "#8B5CF6", "Internet, electricidad, agua y telefonía"),
    ("Entretenimiento", "#EC4899", "Cine, música, salidas y juegos"),
    ("Compras", "#14B8A6", "Ropa, electrodomésticos y otros"),
    ("Salud", "#EF4444", "Farmacia, consultorios y emergencias"),
    (CATEGORIA_SIN_CATEGORIZAR, COLOR_SIN_CATEGORIZAR, "Gastos sin una regla aplicable"),
]

REGLAS_INICIALES: list[tuple[str, str, int]] = [
    ("almuerzo", "Alimentación", 10),
    ("desayuno", "Alimentación", 10),
    ("supermercado", "Alimentación", 10),
    ("pasaje", "Transporte", 10),
    ("gasolina", "Transporte", 10),
    ("internet", "Servicios", 10),
    ("electricidad", "Servicios", 10),
]


async def seed(session: AsyncSession) -> None:
    """Crea categorias y reglas que aun no existen (idempotente)."""
    categorias_repo = CategoriaRepository(session)
    reglas_repo = ReglaRepository(session)

    categorias: dict[str, Categoria] = {}
    for nombre, color, descripcion in CATEGORIAS_INICIALES:
        categoria = await categorias_repo.get_by_nombre(nombre)
        if categoria is None:
            categoria = await categorias_repo.create(
                Categoria(
                    nombre=nombre,
                    descripcion=descripcion,
                    color_hex=color,
                    activa=True,
                )
            )
        categorias[nombre] = categoria

    existentes = await reglas_repo.listar()
    for palabra_clave, categoria_nombre, prioridad in REGLAS_INICIALES:
        categoria = categorias[categoria_nombre]
        ya_existe = any(
            regla.palabra_clave.casefold() == palabra_clave.casefold()
            and regla.categoria_id == categoria.id
            for regla in existentes
        )
        if ya_existe:
            continue
        await reglas_repo.create(
            Regla(
                palabra_clave=palabra_clave,
                categoria_id=categoria.id,
                prioridad=prioridad,
                activa=True,
            )
        )
        existentes.append(
            Regla(
                palabra_clave=palabra_clave,
                categoria_id=categoria.id,
                prioridad=prioridad,
                activa=True,
            )
        )

    await session.commit()


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed(session)
    await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
