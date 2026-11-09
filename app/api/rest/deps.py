"""
REST-specific dependencies.

These provide assembled domain services to route handlers via FastAPI's Depends().
Database sessions are managed transparently by middleware and the repository layer;
no database sessions or repositories are referenced in this layer.
"""

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.api.constants import AUTH_TOKEN_URL
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.core.context import set_current_experience
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import (
    InvalidTokenError,
    UserNotActiveError,
    UserNotFoundError,
)
from app.model.identity.app_user import AppUser
from app.service.authentication.current_user_service import CurrentUserService
from app.service.authentication.factory import (
    build_current_user_service,
    build_login_service,
    build_registration_service,
    build_token_refresh_service,
)
from app.service.authentication.login_service import LoginService
from app.service.authentication.registration_service import RegistrationService
from app.service.authentication.token_refresh_service import TokenRefreshService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL)


# ──────────────────────────────────────────────
# REST Service Providers
# ──────────────────────────────────────────────
def get_login_service() -> LoginService:
    """Provide a LoginService instance."""
    return build_login_service()


def get_registration_service() -> RegistrationService:
    """Provide a RegistrationService instance."""
    return build_registration_service()


def get_token_refresh_service() -> TokenRefreshService:
    """Provide a TokenRefreshService instance."""
    return build_token_refresh_service()


def get_current_user_service() -> CurrentUserService:
    """Provide a CurrentUserService instance."""
    return build_current_user_service()


def get_experience_context(
    experience_header: str | None = Header(default=None, alias="Experience"),
    x_experience_header: str | None = Header(default=None, alias="X-Experience"),
) -> Experience:
    """
    Extract the target application experience from the 'Experience' or 'X-Experience' HTTP request header.
    Defaults to Experience.CUSTOMER if the header is omitted.
    Stores the value in ContextVar and returns the parsed Experience.
    """
    raw = experience_header or x_experience_header
    if not raw:
        exp = Experience.CUSTOMER
    else:
        try:
            exp = Experience(raw.strip().upper())
        except ValueError:
            raise HTTPException(
                status_code=HttpCode._400,
                detail=f"Invalid Experience header. Must be one of: {[e.value for e in Experience]}",
            )
    set_current_experience(exp)
    return exp


# ──────────────────────────────────────────────
# Authentication / Identity Route Dependencies
# ──────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    current_user_service: CurrentUserService = Depends(get_current_user_service),
) -> AppUser:
    """
    REST FastAPI dependency — extracts the Bearer token from the Authorization header,
    validates the JWT, and fetches the active AppUser via CurrentUserService.

    Inject into protected routes:
        current_user: AppUser = Depends(get_current_user)

    Raises:
        HTTPException(401): if the token is invalid, expired, or user is not found.
        HTTPException(403): if the user account is not active.
    """
    try:
        return await current_user_service.get_user_from_token(token)
    except (InvalidTokenError, UserNotFoundError):
        raise HTTPException(
            status_code=HttpCode._401,
            detail=HttpMessage.AUTHENTICATION_REQUIRED,
        )
    except UserNotActiveError:
        raise HTTPException(
            status_code=HttpCode._403,
            detail=HttpMessage.ACCOUNT_NOT_ACTIVE,
        )
