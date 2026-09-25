"""
REST-specific dependencies.

These use FastAPI's Depends() mechanism and are coupled to HTTP request handling.
"""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.constants import AUTH_TOKEN_URL
from app.api.deps import get_user_id_from_token
from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.core.database import get_db
from app.model.identity.app_user import AppUser, AppUserStatus
from app.repository.identity.app_user_repo import AppUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AppUser:
    """
    REST FastAPI dependency — extracts the Bearer token from the Authorization header,
    validates the JWT, fetches the AppUser from DB, and returns them.

    Inject into protected routes:
        current_user: AppUser = Depends(get_current_user)

    Raises:
        HTTPException(401): if the token is invalid, expired, or user is not found/active.
    """
    user_id = get_user_id_from_token(token)
    user = await AppUserRepository(db).find_by_id(user_id)

    if user is None or user.status != AppUserStatus.ACTIVE:
        raise HTTPException(
            status_code=HttpCode._401,
            detail=HttpMessage.AUTHENTICATION_REQUIRED,
        )
    return user

