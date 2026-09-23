from collections.abc import Generator
from contextvars import ContextVar, Token

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.audit import register_audit_listeners
from app.core.config import settings


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 Declarative Base class."""


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

# Register audit event listeners across all sessions
register_audit_listeners()

_session_context: ContextVar[Session | None] = ContextVar("session_context", default=None)


def get_current_session() -> Session | None:
    """Return the active database session from the current context, if any."""
    return _session_context.get()


def set_current_session(session: Session | None) -> Token:
    """Set the active database session in the current context."""
    return _session_context.set(session)


def reset_current_session(token: Token) -> None:
    """Reset the database session context."""
    _session_context.reset(token)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    token = set_current_session(db)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        reset_current_session(token)
        db.close()