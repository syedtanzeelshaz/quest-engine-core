"""
User login / credential authentication route handler.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_experience_context
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_login_service
from app.api.rest.routes.auth.helpers import make_token_response
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import InvalidCredentialsError, UserNotActiveError
from app.schema.authentication.auth import LoginRequest, TokenResponse
from app.service.authentication.login_service import LoginService
from app.service.authentication.models import LoginCommand
from app.util.logger import log

router = APIRouter()


@router.post("/login", response_model=TokenResponse, status_code=HttpCode._200)
async def login(
    body: LoginRequest,
    experience: Experience = Depends(get_experience_context),
    login_service: LoginService = Depends(get_login_service),
) -> TokenResponse:
    """Authenticate user credentials and return JWT tokens."""
    log.info("Received login request for email: %s, experience: %s", body.email, experience)

    try:
        _, token_pair = await login_service.authenticate(
            LoginCommand(
                email=body.email,
                plain_password=body.password.get_secret_value(),
                experience=experience,
            )
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

    return make_token_response(token_pair)

