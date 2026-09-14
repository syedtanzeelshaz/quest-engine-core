from sqlalchemy import text
from app.core.database import SessionLocal
from app.util.logger import log

def check_database_connection() -> None:
    log.info("Running database connectivity check...")
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        log.info("Database connectivity check passed successfully.")
    except Exception as e:
        log.error(f"CRITICAL: Database connectivity check failed: {e}")
        raise e
    finally:
        db.close()