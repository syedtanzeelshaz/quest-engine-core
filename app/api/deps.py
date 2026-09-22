"""
Shared API dependencies -- used across all transports (REST, GraphQL, WebSocket).
"""
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.constants.http_codes import HttpCode
from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, reset_current_session, set_current_session
from app.core.exceptions import InvalidRefreshTokenError
from app.service.authentication.token import TokenService

_token_service = TokenService(settings)


def get_db() -> Generator[Session, None, None]:
    """
    Shared database session dependency.
    Used by REST route handlers, GraphQL context builder, and WebSocket handlers.
    """
    db = SessionLocal()
    token = set_current_session(db)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        reset_current_session(token)
        db.close()


def get_user_id_from_token(raw_token: str) -> int:
    """
    Verify a JWT access token string and return the user_id.

    Pure helper with no FastAPI coupling -- shared by REST deps and future
    GraphQL context setup.

    Raises:
        HTTPException(401): if the token is invalid or expired.
    """
    try:
        return _token_service.verify_access_token(raw_token)
    except InvalidRefreshTokenError:
        raise HTTPException(status_code=HttpCode.UNAUTHORIZED, detail=HttpMessage.INVALID_TOKEN)
