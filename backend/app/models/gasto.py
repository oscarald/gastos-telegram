from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import Origen

if TYPE_CHECKING:
    from app.models.categoria import Categoria


class Gasto(Base, TimestampMixin):
    __tablename__ = "gastos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="BOB",
        server_default="BOB",
    )
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True,
    )
    metodo_pago: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    origen: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=Origen.TELEGRAM.value,
        server_default=Origen.TELEGRAM.value,
    )
    identificador_externo: Mapped[str | None] = mapped_column(String(128), nullable=True)

    categoria: Mapped[Categoria] = relationship(back_populates="gastos", lazy="joined")

    __table_args__ = (
        CheckConstraint("origen IN ('telegram', 'web')", name="origen_valido"),
        Index(
            "uq_gastos_identificador_externo",
            "identificador_externo",
            unique=True,
            postgresql_where=text("identificador_externo IS NOT NULL"),
        ),
        Index("ix_gastos_categoria_id_fecha", "categoria_id", "fecha"),
        Index("ix_gastos_fecha_descripcion", "fecha", "descripcion"),
    )

    def __repr__(self) -> str:  # pragma: no cover - ayuda en debugging
        return f"<Gasto id={self.id} monto={self.monto} descripcion={self.descripcion!r}>"
