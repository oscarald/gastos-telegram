"""Tablas categorias, gastos y reglas

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-02

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("color_hex", sa.String(length=7), nullable=False),
        sa.Column("activa", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_categorias"),
    )
    op.create_index("ix_categorias_nombre", "categorias", ["nombre"], unique=True)

    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("moneda", sa.String(length=3), server_default="BOB", nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column(
            "fecha",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("metodo_pago", sa.String(length=50), nullable=True),
        sa.Column("origen", sa.String(length=20), server_default="telegram", nullable=False),
        sa.Column("identificador_externo", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "origen IN ('telegram', 'web')",
            name="ck_gastos_origen_valido",
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias.id"],
            name="fk_gastos_categoria_id_categorias",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_gastos"),
    )
    op.create_index("ix_gastos_categoria_id", "gastos", ["categoria_id"])
    op.create_index("ix_gastos_categoria_id_fecha", "gastos", ["categoria_id", "fecha"])
    op.create_index("ix_gastos_fecha", "gastos", ["fecha"])
    op.create_index("ix_gastos_fecha_descripcion", "gastos", ["fecha", "descripcion"])
    op.create_index("ix_gastos_metodo_pago", "gastos", ["metodo_pago"])
    op.create_index(
        "uq_gastos_identificador_externo",
        "gastos",
        ["identificador_externo"],
        unique=True,
        postgresql_where=sa.text("identificador_externo IS NOT NULL"),
    )

    op.create_table(
        "reglas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("palabra_clave", sa.String(length=100), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.Column("prioridad", sa.Integer(), server_default="0", nullable=False),
        sa.Column("activa", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias.id"],
            name="fk_reglas_categoria_id_categorias",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reglas"),
        sa.UniqueConstraint(
            "palabra_clave",
            "categoria_id",
            name="uq_reglas_palabra_categoria",
        ),
    )
    op.create_index("ix_reglas_categoria_id", "reglas", ["categoria_id"])
    op.create_index("ix_reglas_palabra_clave", "reglas", ["palabra_clave"])


def downgrade() -> None:
    op.drop_index("ix_reglas_palabra_clave", table_name="reglas")
    op.drop_index("ix_reglas_categoria_id", table_name="reglas")
    op.drop_table("reglas")

    op.drop_index("uq_gastos_identificador_externo", table_name="gastos")
    op.drop_index("ix_gastos_metodo_pago", table_name="gastos")
    op.drop_index("ix_gastos_fecha_descripcion", table_name="gastos")
    op.drop_index("ix_gastos_fecha", table_name="gastos")
    op.drop_index("ix_gastos_categoria_id_fecha", table_name="gastos")
    op.drop_index("ix_gastos_categoria_id", table_name="gastos")
    op.drop_table("gastos")

    op.drop_index("ix_categorias_nombre", table_name="categorias")
    op.drop_table("categorias")
