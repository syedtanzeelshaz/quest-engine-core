from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.util.logger import log

""" Lightweight SQL query used to verify database connectivity during startup checks. """
DB_PING_QUERY = text("SELECT 1")


async def check_database_connection() -> None:
    log.info("Running database connectivity check...")
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(DB_PING_QUERY)
            log.info("Database connectivity check passed successfully.")
        except Exception as e:
            log.error(f"CRITICAL: Database connectivity check failed: {e}")
            raise