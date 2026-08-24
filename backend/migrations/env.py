from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = current_app.extensions["migrate"].db.metadata
MANAGED_TABLES = {
    "alembic_version",
    "audit_events",
    "device_push_tokens",
    "idempotency_records",
    "operator_lots",
    "parking_lots",
    "parking_spots",
    "payments",
    "refresh_sessions",
    "reservations",
    "users",
    "vehicles",
    "webhook_events",
}


def include_object(_object, name: str, type_: str, _reflected, _compare_to) -> bool:
    """Exclude PostGIS/tiger extension objects while retaining every app table."""
    return type_ != "table" or name in MANAGED_TABLES


def get_url() -> str:
    return str(current_app.extensions["migrate"].db.engine.url).replace("%", "%%")


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = current_app.extensions["migrate"].db.engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
