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
