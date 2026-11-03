"""Motor de categorizacion automatica.

La logica de coincidencia vive aislada en este modulo para poder mejorarla
(pronombres, sinonimos, machine learning) sin tocar los controladores HTTP.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CATEGORIA_SIN_CATEGORIZAR, COLOR_SIN_CATEGORIZAR
from app.models.categoria import Categoria
from app.models.regla import Regla
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.regla_repository import ReglaRepository

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normaliza texto para comparar: sin acentos, sin mayusculas, sin espacios extra.

    >>> normalize_text("  Almuerzo  con  ÑOÑO ")
    'almuerzo con nono'
    """
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _WHITESPACE_RE.sub(" ", without_accents.casefold()).strip()


def matches_keyword(normalized_text: str, normalized_keyword: str) -> bool:
    """True si la palabra clave aparece completa dentro del texto.

    Usa limites de palabra para evitar coincidencias por fragmentos
    ('almuerzo' no coincide con 'almuerzos' ni con 'xalmuerzo').
    """
    if not normalized_keyword:
        return False
    pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


@dataclass(frozen=True)
class Coincidencia:
    regla_id: int
    palabra_clave: str
    prioridad: int
    categoria_id: int
    categoria_nombre: str


def select_best_rule(descripcion: str, reglas: list[Regla]) -> Regla | None:
    """Devuelve la regla con mayor prioridad que coincide con la descripcion.

    Desempate: prioridad desc, luego longitud de la palabra clave desc
    (la mas especifica gana) y finalmente id asc.
    """
    normalized_description = normalize_text(descripcion)
    candidatos: list[tuple[Regla, str]] = []

    for regla in reglas:
        if not regla.activa:
            continue
        categoria = regla.categoria
        if categoria is None or not categoria.activa:
            continue
        palabra = normalize_text(regla.palabra_clave)
        if matches_keyword(normalized_description, palabra):
            candidatos.append((regla, palabra))

    if not candidatos:
        return None

    candidatos.sort(key=lambda item: (-item[0].prioridad, -len(item[1]), item[0].id))
    return candidatos[0][0]


def find_matches(descripcion: str, reglas: list[Regla]) -> list[Coincidencia]:
    """Todas las reglas que coinciden (util para diagnostico)."""
    normalized_description = normalize_text(descripcion)
    coincidencias = [
        Coincidencia(
            regla_id=regla.id,
            palabra_clave=normalize_text(regla.palabra_clave),
            prioridad=regla.prioridad,
            categoria_id=regla.categoria_id,
            categoria_nombre=regla.categoria.nombre if regla.categoria else "",
        )
        for regla in reglas
        if regla.activa
        and regla.categoria is not None
        and regla.categoria.activa
        and matches_keyword(normalized_description, normalize_text(regla.palabra_clave))
    ]
    coincidencias.sort(key=lambda item: (-item.prioridad, -len(item.palabra_clave), item.regla_id))
    return coincidencias


class CategorizationService:
    """Resuelve la categoria de un gasto usando las reglas configuradas."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reglas_repo = ReglaRepository(session)
        self.categorias_repo = CategoriaRepository(session)

    async def resolver_categoria(self, descripcion: str) -> Categoria:
        """Categoria asignada segun las reglas activas de la descripcion."""
        reglas = await self.reglas_repo.listar(solo_activas=True)
        regla = select_best_rule(descripcion, reglas)
        if regla is not None and regla.categoria is not None:
            return regla.categoria
        return await self.obtener_categoria_sin_categorizar()

    async def obtener_categoria_sin_categorizar(self) -> Categoria:
        """Categoria por defecto; se crea (o reactiva) si no existe."""
        categoria = await self.categorias_repo.get_by_nombre(CATEGORIA_SIN_CATEGORIZAR)
        if categoria is None:
            categoria = await self.categorias_repo.create(
                Categoria(
                    nombre=CATEGORIA_SIN_CATEGORIZAR,
                    descripcion="Gastos sin una regla aplicable",
                    color_hex=COLOR_SIN_CATEGORIZAR,
                    activa=True,
                )
            )
        elif not categoria.activa:
            categoria.activa = True
            await self.session.flush()
        return categoria
