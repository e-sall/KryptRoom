from alembic import context
from sqlalchemy import create_engine, pool

from kryptroom_control.config import load_settings
from kryptroom_control.db import SCHEMA, Base

settings = load_settings()
options = {
    "target_metadata": Base.metadata,
    "version_table_schema": SCHEMA,
    "include_schemas": True,
    "include_name": lambda name, type_, parent: name == SCHEMA if type_ == "schema" else True,
}

if context.is_offline_mode():
    context.configure(
        url=settings.database_url(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **options,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(
        settings.database_url(),
        poolclass=pool.NullPool,
        hide_parameters=True,
        connect_args={
            "connect_timeout": settings.database_connect_timeout,
            "options": "-c lock_timeout=5000 -c statement_timeout=10000",
        },
    )
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, **options)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
