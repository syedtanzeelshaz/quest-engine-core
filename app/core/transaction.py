import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from app.core.database import (
    SessionLocal,
    get_current_session,
    reset_current_session,
    set_current_session,
)

F = TypeVar("F", bound=Callable[..., Any])


def _resolve_session(*args: Any, **kwargs: Any) -> tuple[Session | None, bool]:
    """Resolve an active database session.

    Returns:
        tuple[Session | None, bool]: (session, is_newly_created)
    """
    # 1. Check ContextVar (e.g. injected via get_db dependency or parent caller)
    session = get_current_session()
    if session is not None and isinstance(session, Session):
        return session, False

    # 2. Check kwargs for explicit 'session' or 'db'
    for key in ("session", "db"):
        candidate = kwargs.get(key)
        if candidate is not None and isinstance(candidate, Session):
            return candidate, False

    # 3. Check 'self' in args (service or handler instance)
    if args:
        self_obj = args[0]
        # Direct self.session
        candidate = getattr(self_obj, "session", None)
        if candidate is not None and isinstance(candidate, Session):
            return candidate, False

        # Injected repositories on self (e.g. self.user_repo.session)
        for attr_val in vars(self_obj).values():
            try:
                repo_session = getattr(attr_val, "session", None)
                if repo_session is not None and isinstance(repo_session, Session):
                    return repo_session, False
            except Exception:
                continue

    # 4. Fallback: instantiate a new SessionLocal
    new_session = SessionLocal()
    return new_session, True


def transactional(func: F) -> F:
    """Decorator providing declarative database transaction boundary management.

    - Joins the current active transaction or opens a new one.
    - If a transaction is already active, creates a SAVEPOINT (nested transaction).
    - Automatically commits on successful exit.
    - Automatically rolls back if an unhandled exception is raised.
    - Works with both synchronous and asynchronous functions.
    """
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            session, is_new = _resolve_session(*args, **kwargs)
            token = set_current_session(session) if session else None
            try:
                if session is None:
                    return await func(*args, **kwargs)

                if session.in_transaction():
                    with session.begin_nested():
                        return await func(*args, **kwargs)
                else:
                    with session.begin():
                        return await func(*args, **kwargs)
            finally:
                if token is not None:
                    reset_current_session(token)
                if is_new and session is not None:
                    session.close()

        return async_wrapper  # type: ignore

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        session, is_new = _resolve_session(*args, **kwargs)
        token = set_current_session(session) if session else None
        try:
            if session is None:
                return func(*args, **kwargs)

            if session.in_transaction():
                with session.begin_nested():
                    return func(*args, **kwargs)
            else:
                with session.begin():
                    return func(*args, **kwargs)
        finally:
            if token is not None:
                reset_current_session(token)
            if is_new and session is not None:
                session.close()

    return sync_wrapper  # type: ignore
