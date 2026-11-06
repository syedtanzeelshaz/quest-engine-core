from collections.abc import AsyncGenerator
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.audit import register_audit_listeners
from app.core.config import settings

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Request-scoped database session and transaction lifecycle management via ContextVar
class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages an asynchronous database session per HTTP request.
    Stores the session in ContextVar for the duration of the request.
    Automatically commits on successful 2xx/3xx response, rolls back on error or 4xx/5xx.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # If an active session is already present (e.g. injected in test fixtures), proceed
        if get_current_session() is not None:
            return await call_next(request)

        async with AsyncSessionLocal() as session:
            token = set_current_session(session)
            try:
                response = await call_next(request)
                if response.status_code >= 400:
                    await session.rollback()
                else:
                    await session.commit()
                return response
            except Exception:
                await session.rollback()
                raise
            finally:
                reset_current_session(token)


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0 Declarative Base class."""


# Primary asynchronous database engine powered by asyncpg
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_timeout=30,
)

# Asynchronous session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Register audit event listeners across all sessions
register_audit_listeners()

_session_context: ContextVar[AsyncSession | None] = ContextVar("session_context", default=None)


def get_current_session() -> AsyncSession | None:
    """Return the active database session from the current context, if any."""
    return _session_context.get()


def set_current_session(session: AsyncSession | None) -> Token:
    """Set the active database session in the current context."""
    return _session_context.set(session)


def reset_current_session(token: Token | None = None) -> None:
    """Reset the database session context."""
    if token is not None:
        try:
            _session_context.reset(token)
            return
        except ValueError:
            pass
    _session_context.set(None)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an asynchronous database session per request."""
    async with AsyncSessionLocal() as db:
        token = set_current_session(db)
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            reset_current_session(token)

