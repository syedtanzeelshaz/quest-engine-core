"""
CurrentUserService — resolves and validates the authenticated user from access tokens.

Coordinates token cryptographic verification with user account existence and status checks.
"""

from app.core.primitives.exceptions import (
    InvalidTokenError,
    UserNotActiveError,
    UserNotFoundError,
)
from app.model.identity.app_user import AppUser, AppUserStatus
from app.repository.identity.app_user_repo import AppUserRepository
from app.service.authentication.token import TokenService


class CurrentUserService:
    """Resolves and validates the active authenticated user."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service

    async def get_user_from_token(self, raw_token: str) -> AppUser:
        """
        Verify an access token and return the active AppUser entity.

        Raises:
            InvalidTokenError: If token is expired, malformed, or not an access token.
            UserNotFoundError: If the user ID in the token does not exist.
            UserNotActiveError: If the user account exists but is not ACTIVE.
        """
        user_id = self._token_service.verify_access_token(raw_token)
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} does not exist.")

        if user.status != AppUserStatus.ACTIVE:
            raise UserNotActiveError(
                f"User account is not active (status={user.status})."
            )

        return user

    async def get_active_user_by_id(self, user_id: int) -> AppUser:
        """
        Fetch an active AppUser by their primary key ID.

        Raises:
            UserNotFoundError: If the user ID does not exist.
            UserNotActiveError: If the user account exists but is not ACTIVE.
        """
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} does not exist.")

        if user.status != AppUserStatus.ACTIVE:
            raise UserNotActiveError(
                f"User account is not active (status={user.status})."
            )

        return user

