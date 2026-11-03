"""Fixtures de las pruebas de integracion (requieren PostgreSQL)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from app.db.seed import seed
from app.db.session import get_db
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parents[2]
URL_BASE = "http://testserver"


@pytest.fixture(scope="session", autouse=True)
def aplicar_migraciones() -> None:
    """Crea el esquema real (Alembic) en la base de datos de pruebas."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
    command.downgrade(config, "base")
    command.upgrade(config, "head")


@pytest_asyncio.fixture(scope="session")
async def engine():
    test_engine = create_async_engine(os.environ["DATABASE_URL"], poolclass=NullPool)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncSession:
    """Sesion limpia con categorias y reglas iniciales."""
    async with engine.begin() as connection:
        await connection.execute(
            text("TRUNCATE TABLE gastos, reglas, categorias RESTART IDENTITY CASCADE")
        )
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with factory() as session:
        await seed(session)
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Cliente HTTP contra la aplicacion con la sesion de pruebas inyectada."""

    async def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=URL_BASE) as test_client:
        yield test_client
    app.dependency_overrides.clear()
