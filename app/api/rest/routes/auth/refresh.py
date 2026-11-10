"""
Token refresh route handler.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_token_refresh_service
from app.api.rest.routes.auth.helpers import make_token_response
from app.core.primitives.exceptions import InvalidRefreshTokenError
from app.schema.authentication.auth import RefreshRequest, TokenResponse
from app.service.authentication.token_refresh_service import TokenRefreshService
from app.util.logger import log

router = APIRouter()


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

    return make_token_response(token_pair)

