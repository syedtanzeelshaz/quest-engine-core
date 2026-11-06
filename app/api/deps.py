"""
Shared API dependencies.
"""
from fastapi import HTTPException

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.core.primitives.exceptions import InvalidTokenError
from app.service.authentication.factory import get_token_service


def get_user_id_from_token(raw_token: str) -> int:
    """
    Verify a JWT access token string and return the associated user ID.

    Raises:
        HTTPException(401): If the token is invalid or expired.
    """
    try:
        return get_token_service().verify_access_token(raw_token)
    except InvalidTokenError:
        raise HTTPException(status_code=HttpCode._401, detail=HttpMessage.INVALID_TOKEN)
