import os

from alembic.config import Config

from alembic import command
from app.util.logger import log


def run_database_migrations() -> None:
    """
    Programmatically runs pending Alembic database migrations up to 'head'.
    """
    log.info("Checking and applying pending database migrations...")

    # Resolve the path to alembic.ini at the project root
    # (adjust path resolution depth based on where your root is)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    alembic_ini_path = os.path.join(project_root, "alembic.ini")

    if not os.path.exists(alembic_ini_path):
        error_msg = f"Alembic configuration file not found at: {alembic_ini_path}"
        log.error(error_msg)
        raise FileNotFoundError(error_msg)

    # Initialize Alembic configuration object
    alembic_cfg = Config(alembic_ini_path)

    # Prevent Alembic from reconfiguring the application's existing logging setup.
    alembic_cfg.attributes["skip_logging_config"] = True

    try:
        # Programmatically execute 'alembic upgrade head'
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        log.error(f"CRITICAL: Database migration execution failed: {e}")
        raise
    finally:
        log.info("Database migration initialization block completed.")

    log.info("Database migrations applied successfully.")