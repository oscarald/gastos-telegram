from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.categoria import Categoria


class Regla(Base, TimestampMixin):
    __tablename__ = "reglas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    palabra_clave: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    prioridad: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    categoria: Mapped[Categoria] = relationship(back_populates="reglas", lazy="joined")

    __table_args__ = (
        UniqueConstraint("palabra_clave", "categoria_id", name="uq_reglas_palabra_categoria"),
    )

    def __repr__(self) -> str:  # pragma: no cover - ayuda en debugging
        return f"<Regla id={self.id} palabra_clave={self.palabra_clave!r}>"
