import functools
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import (
    AsyncSessionLocal,
    get_current_session,
    reset_current_session,
    set_current_session,
)

F = TypeVar("F", bound=Callable[..., Any])


def _resolve_session(*args: Any, **kwargs: Any) -> tuple[AsyncSession, bool]:
    """
    Resolve an active asynchronous database session.

    Resolution order:
        1. ContextVar (e.g. injected via get_db dependency per request)
        2. Explicit keyword arguments ('session' or 'db')
        3. Injected on 'self' (self.session or repository on self)
        4. Fallback: instantiate a new session from AsyncSessionLocal

    Returns:
        tuple[AsyncSession, bool]: (session, is_newly_created)
    """
    # 1. Check ContextVar
    session = get_current_session()
    if session is not None:
        return session, False

    # 2. Check keyword arguments
    for key in ("session", "db"):
        candidate = kwargs.get(key)
        if candidate is not None:
            return candidate, False

    # 3. Check 'self' in positional args
    if args:
        self_obj = args[0]
        candidate = getattr(self_obj, "session", None)
        if candidate is not None:
            return candidate, False

        # Injected repositories on self (e.g. self._user_repo.session)
        if hasattr(self_obj, "__dict__"):
            for attr_val in vars(self_obj).values():
                repo_session = getattr(attr_val, "session", None)
                if repo_session is not None:
                    return repo_session, False

    # 4. Fallback: instantiate a new session
    return AsyncSessionLocal(), True


def transactional(func: F) -> F:
    """
    Decorator providing declarative database transaction boundary management for async functions.

    - Joins the current active transaction or opens a new one.
    - If a transaction is already active, creates a SAVEPOINT (nested transaction).
    - Automatically commits on successful exit.
    - Automatically rolls back if an unhandled exception is raised.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        session, is_new = _resolve_session(*args, **kwargs)
        token = set_current_session(session)
        try:
            if session.in_transaction():
                async with session.begin_nested():
                    return await func(*args, **kwargs)
            else:
                async with session.begin():
                    return await func(*args, **kwargs)
        finally:
            reset_current_session(token)
            if is_new:
                await session.close()

    return wrapper  # type: ignore
