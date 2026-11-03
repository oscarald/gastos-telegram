from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ReglaNegocioError
from app.core.timezone import day_bounds_utc, default_zone, month_bounds_utc
from app.models.enums import Origen
from app.models.gasto import Gasto
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.gasto_repository import FiltrosGasto, GastoRepository
from app.schemas.gasto import GastoCreate, GastoTelegramCreate, GastoUpdate
from app.services.categorization_service import CategorizationService


def parse_fecha(valor: str) -> date | datetime:
    """Interpreta una fecha en formato ISO (fecha o fecha-hora)."""
    texto = valor.strip()
    if not texto:
        raise ReglaNegocioError("La fecha no puede estar vacia")
    try:
        if "T" in texto or " " in texto:
            return datetime.fromisoformat(texto.replace(" ", "T"))
        return date.fromisoformat(texto)
    except ValueError as exc:
        raise ReglaNegocioError(f"Fecha invalida: {valor}") from exc


def _a_utc_inicio(valor: date | datetime, zone: ZoneInfo) -> datetime:
    if isinstance(valor, datetime):
        localizado = valor if valor.tzinfo is not None else valor.replace(tzinfo=zone)
        return localizado.astimezone(timezone.utc)
    return day_bounds_utc(valor, zone)[0]


def _a_utc_fin(valor: date | datetime, zone: ZoneInfo) -> datetime:
    if isinstance(valor, datetime):
        localizado = valor if valor.tzinfo is not None else valor.replace(tzinfo=zone)
        return localizado.astimezone(timezone.utc)
    return day_bounds_utc(valor, zone)[1]


class GastoService:
    """Reglas de negocio para registrar, consultar y modificar gastos."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.gastos_repo = GastoRepository(session)
        self.categorias_repo = CategoriaRepository(session)
        self.categorizador = CategorizationService(session)

    # ------------------------------------------------------------------
    # Resolucion de filtros
    # ------------------------------------------------------------------
    def construir_filtros(
        self,
        mes: int | None = None,
        anio: int | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        categoria_id: int | None = None,
        metodo_pago: str | None = None,
        origen: str | None = None,
        busqueda: str | None = None,
    ) -> FiltrosGasto:
        zone = default_zone()
        inicio: datetime | None = None
        fin: datetime | None = None

        if mes is not None and anio is not None:
            inicio_mes, fin_mes = month_bounds_utc(anio, mes, zone)
            inicio = inicio_mes
            fin = fin_mes

        if fecha_desde:
            limite_inferior = _a_utc_inicio(parse_fecha(fecha_desde), zone)
            inicio = limite_inferior if inicio is None else max(inicio, limite_inferior)

        if fecha_hasta:
            limite_superior = _a_utc_fin(parse_fecha(fecha_hasta), zone)
            fin = limite_superior if fin is None else min(fin, limite_superior)

        if mes is not None and anio is None:
            raise ReglaNegocioError("Debes indicar el anio cuando specifies el mes")
        if anio is not None and mes is None:
            raise ReglaNegocioError("Debes indicar el mes cuando specifics el anio")

        return FiltrosGasto(
            fecha_desde=inicio,
            fecha_hasta=fin,
            categoria_id=categoria_id,
            metodo_pago=metodo_pago or None,
            origen=origen or None,
            busqueda=(busqueda or "").strip() or None,
        )

    # ------------------------------------------------------------------
    # Alta de gastos
    # ------------------------------------------------------------------
    async def _resolver_categoria(self, categoria_id: int | None, descripcion: str):
        if categoria_id is None:
            return await self.categorizador.resolver_categoria(descripcion)
        categoria = await self.categorias_repo.get_by_id(categoria_id)
        if categoria is None:
            raise NotFoundError(f"No existe la categoria con id {categoria_id}")
        if not categoria.activa:
            raise ReglaNegocioError(f"La categoria '{categoria.nombre}' esta desactivada")
        return categoria

    async def registrar_manual(self, payload: GastoCreate) -> Gasto:
        categoria = await self._resolver_categoria(payload.categoria_id, payload.descripcion)
        gasto = Gasto(
            monto=payload.monto,
            moneda=payload.moneda,
            descripcion=payload.descripcion,
            categoria=categoria,
            fecha=payload.fecha or datetime.now(timezone.utc),
            metodo_pago=payload.metodo_pago,
            origen=Origen.WEB.value,
        )
        await self.gastos_repo.create(gasto)
        await self.session.commit()
        return gasto

    async def registrar_desde_telegram(self, payload: GastoTelegramCreate) -> tuple[Gasto, bool]:
        """Registra un gasto de Telegram. Devuelve (gasto, es_duplicado)."""
        identificador = (payload.identificador_externo or "").strip() or None

        if identificador:
            existente = await self.gastos_repo.get_by_identificador_externo(identificador)
            if existente is not None:
                return existente, True

        categoria = await self.categorizador.resolver_categoria(payload.descripcion)
        gasto = Gasto(
            monto=payload.monto,
            moneda=payload.moneda,
            descripcion=payload.descripcion,
            categoria=categoria,
            fecha=payload.fecha or datetime.now(timezone.utc),
            metodo_pago=payload.metodo_pago,
            origen=Origen.TELEGRAM.value,
            identificador_externo=identificador,
        )

        try:
            await self.gastos_repo.create(gasto)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            if identificador:
                existente = await self.gastos_repo.get_by_identificador_externo(identificador)
                if existente is not None:
                    return existente, True
            raise

        return gasto, False

    # ------------------------------------------------------------------
    # Consulta y modificacion
    # ------------------------------------------------------------------
    async def obtener(self, gasto_id: int) -> Gasto:
        gasto = await self.gastos_repo.get_by_id(gasto_id)
        if gasto is None:
            raise NotFoundError(f"No existe el gasto con id {gasto_id}")
        return gasto

    async def listar(
        self,
        filtros: FiltrosGasto,
        orden: str = "fecha_desc",
        pagina: int = 1,
        limite: int = 20,
    ) -> tuple[list[Gasto], int]:
        return await self.gastos_repo.listar(filtros, orden=orden, pagina=pagina, limite=limite)

    async def listar_todos(self, filtros: FiltrosGasto, orden: str = "fecha_desc") -> list[Gasto]:
        return await self.gastos_repo.listar_todos(filtros, orden=orden)

    async def actualizar(self, gasto_id: int, payload: GastoUpdate) -> Gasto:
        gasto = await self.obtener(gasto_id)
        datos = payload.model_dump(exclude_unset=True)

        if "monto" in datos and datos["monto"] is not None:
            gasto.monto = datos["monto"]
        if "descripcion" in datos and datos["descripcion"] is not None:
            gasto.descripcion = datos["descripcion"]
        if "fecha" in datos and datos["fecha"] is not None:
            gasto.fecha = datos["fecha"]
        if "metodo_pago" in datos:
            gasto.metodo_pago = datos["metodo_pago"]
        if "moneda" in datos and datos["moneda"] is not None:
            gasto.moneda = datos["moneda"]

        if "categoria_id" in datos:
            if datos["categoria_id"] is None:
                gasto.categoria = await self.categorizador.resolver_categoria(gasto.descripcion)
            else:
                categoria = await self._resolver_categoria(
                    datos["categoria_id"],
                    gasto.descripcion,
                )
                gasto.categoria = categoria
        elif "descripcion" in datos:
            gasto.categoria = await self.categorizador.resolver_categoria(gasto.descripcion)

        await self.session.commit()
        return gasto

    async def eliminar(self, gasto_id: int) -> None:
        gasto = await self.obtener(gasto_id)
        await self.gastos_repo.delete(gasto)
        await self.session.commit()


def filtros_con_rango(filtros: FiltrosGasto, inicio: datetime, fin: datetime) -> FiltrosGasto:
    """Copia de los filtros con un rango de fechas adicional."""
    return replace(
        filtros,
        fecha_desde=max(filtros.fecha_desde, inicio) if filtros.fecha_desde else inicio,
        fecha_hasta=min(filtros.fecha_hasta, fin) if filtros.fecha_hasta else fin,
    )
