"""
Authentication domain value objects.

Pure Python dataclasses — no FastAPI, no SQLAlchemy, no Pydantic.
These are the internal command/result types passed between auth services.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterCommand:
    """Input data for user registration."""
    email: str
    plain_password: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class LoginCommand:
    """Input data for user authentication."""
    email: str
    plain_password: str


@dataclass(frozen=True)
class AuthTokenPair:
    """Issued JWT access + refresh token pair."""
    access_token: str
    refresh_token: str
    expires_in: int  # access token TTL in seconds


@dataclass(frozen=True)
class CurrentUser:
    """
    Authenticated user context for requests.

    Used across GraphQL context, authorization policies, and service layers.
    """
    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    org_id: int | None = None
    roles: tuple[str, ...] = ()

