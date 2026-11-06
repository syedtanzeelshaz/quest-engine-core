from fastapi import APIRouter, Depends, HTTPException

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import (
    get_current_user,
    get_login_service,
    get_registration_service,
    get_token_refresh_service,
)
from app.core.primitives.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotActiveError,
)
from app.model.identity.app_user import AppUser
from app.schema.authentication.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.service.authentication.login_service import LoginService
from app.service.authentication.models import LoginCommand, RegisterCommand
from app.service.authentication.registration_service import RegistrationService
from app.service.authentication.token_refresh_service import TokenRefreshService
from app.util.logger import log

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _make_token_response(token_pair) -> TokenResponse:
    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )


@router.post("/register", response_model=RegisterResponse, status_code=HttpCode._201)
async def register(
    body: RegisterRequest,
    registration_service: RegistrationService = Depends(get_registration_service),
) -> RegisterResponse:
    """Register a new user account and return JWT tokens."""
    log.info("Received registration request for email: %s", body.email)

    try:
        user, token_pair = await registration_service.register(
            RegisterCommand(
                email=body.email,
                plain_password=body.password,
                first_name=body.first_name,
                last_name=body.last_name,
            )
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=HttpCode._409,
            detail=HttpMessage.EMAIL_ALREADY_REGISTERED,
        )

    return RegisterResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tokens=_make_token_response(token_pair),
    )


@router.post("/login", response_model=TokenResponse, status_code=HttpCode._200)
async def login(
    body: LoginRequest,
    login_service: LoginService = Depends(get_login_service),
) -> TokenResponse:
    """Authenticate user credentials and return JWT tokens."""
    log.info("Received login request for email: %s", body.email)

    try:
        _, token_pair = await login_service.authenticate(
            LoginCommand(email=body.email, plain_password=body.password)
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=HttpCode._401,
            detail=HttpMessage.INVALID_CREDENTIALS,
        )
    except UserNotActiveError:
        raise HTTPException(
            status_code=HttpCode._403,
            detail=HttpMessage.ACCOUNT_NOT_ACTIVE,
        )

    return _make_token_response(token_pair)


@router.post("/refresh", response_model=TokenResponse, status_code=HttpCode._200)
async def refresh_token(
    body: RefreshRequest,
    token_refresh_service: TokenRefreshService = Depends(get_token_refresh_service),
) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    log.info("Received token refresh request.")

    try:
        token_pair = await token_refresh_service.refresh(body.refresh_token)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=HttpCode._401,
            detail=HttpMessage.INVALID_REFRESH_TOKEN,
        )

    return _make_token_response(token_pair)


@router.post("/logout", status_code=HttpCode._200)
async def logout(
    body: LogoutRequest,
    token_refresh_service: TokenRefreshService = Depends(get_token_refresh_service),
    current_user: AppUser = Depends(get_current_user),
) -> dict:
    """
    Revoke the provided refresh token (logout).
    Requires a valid access token in the Authorization header.
    """
    log.info("Received logout request for user_id: %s", current_user.id)

    try:
        await token_refresh_service.revoke(body.refresh_token, requesting_user_id=current_user.id)
    except InvalidRefreshTokenError:
        raise HTTPException(
            status_code=HttpCode._401,
            detail=HttpMessage.INVALID_REFRESH_TOKEN,
        )

    return {"message": HttpMessage.LOGOUT_SUCCESSFUL}
