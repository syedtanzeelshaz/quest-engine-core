"""
Application request-level context variables.

Stores per-request metadata (e.g. current target Experience) across async execution chains.
"""
from contextvars import ContextVar, Token

from app.core.primitives.enums import Experience

_experience_context: ContextVar[Experience | None] = ContextVar(
    "experience_context",
    default=None,
)


def get_current_experience() -> Experience | None:
    """Return the active Experience from the current request context, or None if uninitialized."""
    return _experience_context.get()


def set_current_experience(experience: Experience) -> Token:
    """Set the active Experience in the current request context."""
    return _experience_context.set(experience)


def reset_current_experience(token: Token | None = None) -> None:
    """Reset the Experience context to its previous state using the provided token, or clear to None if omitted."""
    if token is not None:
        try:
            _experience_context.reset(token)
            return
        except ValueError:
            pass
    _experience_context.set(None)

