from app.core.initialization.db_verification import check_database_connection
from app.util.logger import log

def run_startup_checks() -> None:
    log.info("Running application startup bootstrapping...")

    # Execute database ping verification
    check_database_connection()

    # Future boot tasks (e.g., alembic migrations) can be hooked here