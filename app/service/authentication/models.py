"""
Authentication domain value objects.

Pure Python dataclasses. These are the internal command/result types passed between auth services.
"""
from dataclasses import dataclass


from app.core.primitives.enums import Experience


@dataclass(frozen=True)
class RegisterCommand:
    """Input data for user registration."""
    email: str
    plain_password: str
    first_name: str
    last_name: str
    experience: Experience = Experience.CUSTOMER


@dataclass(frozen=True)
class LoginCommand:
    """Input data for user authentication."""
    email: str
    plain_password: str
    experience: Experience = Experience.CUSTOMER


@dataclass(frozen=True)
class AuthTokenPair:
    """Issued JWT access + refresh token pair."""
    access_token: str
    refresh_token: str
    expires_in: int  # access token TTL in seconds

