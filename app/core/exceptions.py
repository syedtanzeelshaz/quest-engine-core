"""
Domain-level exceptions for Quest Engine.

These are pure Python exceptions with no HTTP or FastAPI semantics.
Route handlers are responsible for catching these and translating them
into appropriate HTTPException responses.
"""


class EmailAlreadyExistsError(Exception):
    """Raised when registering with an email address that already exists."""


class InvalidCredentialsError(Exception):
    """
    Raised when login credentials are incorrect.
    Used for both 'email not found' and 'password mismatch' cases — intentionally
    the same exception to prevent user enumeration attacks.
    """


class UserNotActiveError(Exception):
    """Raised when the user account exists but is not in ACTIVE status."""


class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is invalid, expired, or already revoked."""
