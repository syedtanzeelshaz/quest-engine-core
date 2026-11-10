"""
User logout / token revocation route handler.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_current_user, get_token_refresh_service
from app.core.primitives.exceptions import InvalidRefreshTokenError
from app.schema.authentication.auth import LogoutRequest
from app.service.authentication.token_refresh_service import TokenRefreshService
from app.service.user.models import CurrentUser
from app.util.logger import log

router = APIRouter()


@router.post("/logout", status_code=HttpCode._200)
async def logout(
    body: LogoutRequest,
    token_refresh_service: TokenRefreshService = Depends(get_token_refresh_service),
    current_user: CurrentUser = Depends(get_current_user),
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

