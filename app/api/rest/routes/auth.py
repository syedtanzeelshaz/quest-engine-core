from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_current_user
from app.core.config import settings
from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotActiveError,
)
from app.model.identity.app_user import AppUser
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.schema.authentication.auth import (
    LogoutRequest,
    RefreshRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.service.authentication.login import LoginService
from app.service.authentication.models import LoginCommand, RegisterCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.registration import RegistrationService
from app.service.authentication.token import TokenService
from app.service.authentication.token_refresh import TokenRefreshService
from app.util.logger import log

router = APIRouter(prefix="/auth", tags=["Authentication"])

_password_service = PasswordService()
_token_service = TokenService(settings)


def _make_token_response(token_pair) -> TokenResponse:
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )


@router.post("/register", response_model=RegisterResponse, status_code=HttpCode.CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """Register a new user account and return JWT tokens."""
    log.info("Received registration request for email: %s", body.email)

    service = RegistrationService(
        user_repo=AppUserRepository(db),
        refresh_token_repo=RefreshTokenRepository(db),
        password_service=_password_service,
        token_service=_token_service,
    )
    try:
        user, token_pair = service.register(
            RegisterCommand(
                email=body.email,
                plain_password=body.password,
                first_name=body.first_name,
                last_name=body.last_name,
            )
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=HttpCode.CONFLICT,
            detail=HttpMessage.EMAIL_ALREADY_REGISTERED,
        )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tokens=_make_token_response(token_pair),
    )


@router.post("/login", response_model=TokenResponse, status_code=HttpCode.OK)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user credentials and return JWT tokens."""
    log.info("Received login request for email: %s", body.email)

    service = LoginService(
        user_repo=AppUserRepository(db),
        refresh_token_repo=RefreshTokenRepository(db),
        password_service=_password_service,
        token_service=_token_service,
    )
    try:
        _, token_pair = service.authenticate(
            LoginCommand(email=body.email, plain_password=body.password)
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=HttpCode.UNAUTHORIZED,
            detail=HttpMessage.INVALID_CREDENTIALS,
        )
    except UserNotActiveError:
        raise HTTPException(
            status_code=HttpCode.FORBIDDEN,
            detail=HttpMessage.ACCOUNT_NOT_ACTIVE,
        )

    return _make_token_response(token_pair)


@router.post("/refresh", response_model=TokenResponse, status_code=HttpCode.OK)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    log.info("Received token refresh request.")

    service = TokenRefreshService(
        user_repo=AppUserRepository(db),
        refresh_token_repo=RefreshTokenRepository(db),
        token_service=_token_service,
    )
    try:
        token_pair = service.refresh(body.refresh_token)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=HttpCode.UNAUTHORIZED,
            detail=HttpMessage.INVALID_REFRESH_TOKEN,
        )

    return _make_token_response(token_pair)


@router.post("/logout", status_code=HttpCode.OK)
def logout(
    body: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
) -> dict:
    """
    Revoke the provided refresh token (logout).
    Requires a valid access token in the Authorization header.
    """
    log.info("Received logout request for user_id: %s", current_user.id)

    service = TokenRefreshService(
        user_repo=AppUserRepository(db),
        refresh_token_repo=RefreshTokenRepository(db),
        token_service=_token_service,
    )
    try:
        service.revoke(body.refresh_token, requesting_user_id=current_user.id)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=HttpCode.UNAUTHORIZED,
            detail=HttpMessage.INVALID_REFRESH_TOKEN,
        )

    return {"message": HttpMessage.LOGOUT_SUCCESSFUL}
