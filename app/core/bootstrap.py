from app.core.initialization.db_migrations import run_database_migrations
from app.core.initialization.db_verification import check_database_connection
from app.util.logger import log


def run_startup_checks() -> None:
    log.info("Running application startup bootstrapping...")

    # 1. Execute database ping verification
    check_database_connection()

    # 2. Execute pending database migrations
    run_database_migrations()

    log.info("Application startup bootstrapping completed successfully.")