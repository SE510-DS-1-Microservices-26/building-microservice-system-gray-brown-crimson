import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

from src.workflow_service.app.core.infrastructure.database import Base
import src.workflow_service.app.core.infrastructure.models  # noqa: F401 — registers all ORM models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

_raw_database_url = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5435/workflows"
)
# Alembic runs migrations with a synchronous engine; async driver URLs are converted.
if "+asyncpg" in _raw_database_url:
    sync_database_url = _raw_database_url.replace("+asyncpg", "+psycopg", 1)
else:
    sync_database_url = _raw_database_url
config.set_main_option("sqlalchemy.url", sync_database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
