"""
Core domain primitives (enums, constants, and root exceptions).
"""
from app.core.primitives.constants import (
    OrganizationMessage,
    SecurityMessage,
    UserMessage,
)
from app.core.primitives.enums import CountryCode, Gender
from app.core.primitives.exceptions import (
    AccessDeniedError,
    AuthenticationRequiredError,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidInputError,
    InvalidRefreshTokenError,
    InvalidTokenError,
    OrganizationNotFoundError,
    OrganizationRequiredError,
    SlugAlreadyExistsError,
    UserNotActiveError,
    UserNotFoundError,
)

__all__ = [
    "AccessDeniedError",
    "AuthenticationRequiredError",
    "CountryCode",
    "EmailAlreadyExistsError",
    "Gender",
    "InvalidCredentialsError",
    "InvalidInputError",
    "InvalidRefreshTokenError",
    "InvalidTokenError",
    "OrganizationMessage",
    "OrganizationNotFoundError",
    "OrganizationRequiredError",
    "SecurityMessage",
    "SlugAlreadyExistsError",
    "UserMessage",
    "UserNotActiveError",
    "UserNotFoundError",
]
