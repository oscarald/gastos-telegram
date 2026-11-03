from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.gasto import Gasto
    from app.models.regla import Regla


class Categoria(Base, TimestampMixin):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False, default="#6B7280")
    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    gastos: Mapped[list[Gasto]] = relationship(
        back_populates="categoria",
        lazy="selectin",
    )
    reglas: Mapped[list[Regla]] = relationship(
        back_populates="categoria",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - ayuda en debugging
        return f"<Categoria id={self.id} nombre={self.nombre!r}>"
