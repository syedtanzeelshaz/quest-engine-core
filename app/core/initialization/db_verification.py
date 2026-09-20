from sqlalchemy import text

from app.core.database import SessionLocal
from app.util.logger import log

""" Lightweight SQL query used to verify database connectivity during startup checks. """
DB_PING_QUERY = text("SELECT 1")

def check_database_connection() -> None:
    log.info("Running database connectivity check...")
    db = SessionLocal()
    try:
        db.execute(DB_PING_QUERY)
        log.info("Database connectivity check passed successfully.")
    except Exception as e:
        log.error(f"CRITICAL: Database connectivity check failed: {e}")
        raise e
    finally:
        db.close()