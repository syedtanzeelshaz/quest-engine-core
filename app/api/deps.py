"""
Shared API dependencies.
"""
from fastapi import Header, HTTPException

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.core.context import set_current_experience
from app.core.primitives.enums import Experience
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
