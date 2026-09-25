"""
LoginService — user authentication orchestration.

Coordinates credential verification, account status check,
JWT token pair issuance, and refresh token persistence.
"""
from app.core.primitives.exceptions import InvalidCredentialsError, UserNotActiveError
from app.core.transaction import transactional
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair, LoginCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.token import TokenService


class LoginService:
    """Orchestrates user credential authentication and token issuance."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_service: PasswordService,
        token_service: TokenService,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo
        self._password_service = password_service
        self._token_service = token_service
        self._org_member_repo = org_member_repo

    @transactional
    async def authenticate(self, command: LoginCommand) -> tuple[AppUser, AuthTokenPair]:
        """
        Authenticate a user by email and password.

        Steps:
            1. Look up user by email.
            2. Verify password hash.
            3. Check that account is ACTIVE.
            4. Issue JWT access + refresh token pair.
            5. Persist the refresh token hash.

        Returns:
            Tuple of (authenticated AppUser, AuthTokenPair).

        Raises:
            InvalidCredentialsError: if email is not found or password is wrong.
                (Same exception for both cases — prevents user enumeration.)
            UserNotActiveError: if the account exists but is not ACTIVE.
        """
        user = await self._user_repo.find_by_email(command.email)
        if user is None:
            raise InvalidCredentialsError("Invalid email or password.")

        if not await self._password_service.verify(command.plain_password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")

        if user.status != AppUserStatus.ACTIVE:
            raise UserNotActiveError(
                f"User account is not active (status={user.status})."
            )

        roles = await self._org_member_repo.find_roles_by_user(user.id)
        token_roles = roles if roles else None

        token_pair = self._token_service.issue_pair(
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=token_roles,
        )
        await self._persist_refresh_token(user.id, token_pair.refresh_token)

        return user, token_pair

    async def _persist_refresh_token(self, user_id: int, raw_refresh_token: str) -> None:
        token_hash = self._token_service.hash_token(raw_refresh_token)
        expires_at = self._token_service.refresh_token_expires_at()
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self._refresh_token_repo.save_and_flush(refresh_token)
