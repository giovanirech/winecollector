"""Alembic environment — async-aware, reads configuration from
:mod:`winecollector.config` instead of ``alembic.ini``.

Models register themselves on ``winecollector.database.Base.metadata`` as
later tasks add them. Empty metadata is acceptable in V1 wiring."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from winecollector.config import get_settings
from winecollector.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Provide the database URL to Alembic from our Settings layer.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Importing the models package eagerly ensures every model is registered on
# Base.metadata before autogenerate runs. The package will exist starting in
# task_03; the try/except keeps task_02 self-contained.
try:  # pragma: no cover - exercised only after task_03 lands
    import winecollector.models  # noqa: F401
except ImportError:
    pass

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emits SQL to stdout."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode against an async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
