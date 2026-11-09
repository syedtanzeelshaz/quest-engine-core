"""
Core domain primitives (constants and root exceptions).
"""
from app.core.primitives.constants import (
    DatasourceMessage,
    OrganizationMessage,
    SecurityMessage,
    UserMessage,
)
from app.core.primitives.enums import Experience
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
    "DatasourceMessage",
    "EmailAlreadyExistsError",
    "Experience",
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
