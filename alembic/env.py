from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
import app.model  # noqa: F401 - Ensure all models are registered on Base.metadata
from app.core.config import settings
from app.core.database import Base
from app.util.logger import log

# This is the Alembic Config object, which provides access to the values within the alembic.ini file.
config = context.config

# Configure Alembic logging only when it is not being run inside the application.
if (
    config.config_file_name is not None
    and not config.attributes.get("skip_logging_config", False)
):
    fileConfig(config.config_file_name)

# Dynamically inject our application's synchronous database URL into Alembic configuration
config.set_main_option("sqlalchemy.url", settings.ALEMBIC_DATABASE_URL)

# Set target metadata for 'autogenerate' support across our models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine,
    bypassing database connectivity to generate raw SQL scripts.
    Triggered via: alembic upgrade head --sql
    """
    log.info("Running Alembic migrations in OFFLINE mode...")
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"server_side_binding": True},
        include_schemas=True,  # Crucial for multi-schema setup
        version_table="alembic_version",
        version_table_schema="alembic",  # Tracks version in dedicated alembic schema
    )

    with context.begin_transaction():
        context.run_migrations()

    log.info("Alembic offline migration script generation completed.")


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    This creates an Engine and associates a connection with the context,
    executing the migration commands live against the database.
    """
    log.info("Running Alembic migrations in ONLINE mode against live database...")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,  # Crucial for multi-schema setup
            version_table="alembic_version",
            version_table_schema="alembic",  # Tracks version in dedicated alembic schema
        )

        with context.begin_transaction():
            context.run_migrations()

    log.info("Alembic online migrations executed successfully.")


# Automatically route between online or offline mode based on invocation flags
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()