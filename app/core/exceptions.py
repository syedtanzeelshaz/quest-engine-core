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


class InvalidTokenError(Exception):
    """Raised when a JWT access token is invalid, malformed, or expired."""


class InvalidRefreshTokenError(InvalidTokenError):
    """Raised when a refresh token is invalid, expired, or already revoked."""


class UserNotFoundError(Exception):
    """Raised when a user is not found by ID or other identifier."""


class AuthenticationRequiredError(Exception):
    """Raised when an operation requires an authenticated user."""


class OrganizationRequiredError(Exception):
    """Raised when an operation requires active organization membership."""


class AccessDeniedError(Exception):
    """Raised when a user lacks required permissions or roles."""


class OrganizationNotFoundError(Exception):
    """Raised when an organization is not found by ID or slug."""


class SlugAlreadyExistsError(Exception):
    """Raised when creating an organization with a slug that already exists."""


class InvalidInputError(Exception):
    """Raised when user or domain input fails validation constraints."""

