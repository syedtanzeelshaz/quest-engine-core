from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.audit import register_audit_listeners
from app.core.config import settings


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 Declarative Base class."""
    pass


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Register audit event listeners across all sessions
register_audit_listeners()


def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()