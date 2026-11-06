"""
TokenRefreshService — refresh token exchange and revocation (logout).

Handles the full lifecycle of persisted refresh tokens:
  - refresh(): exchange a valid refresh token for a new token pair (with rotation)
  - revoke(): invalidate a refresh token (logout)
"""
from datetime import UTC, datetime

from app.core.primitives.exceptions import InvalidRefreshTokenError
from app.core.transaction import transactional
from app.model.identity.app_user import AppUserStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair
from app.service.authentication.token import TokenService


class TokenRefreshService:
    """Handles refresh token exchange (with rotation) and revocation (logout)."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        refresh_token_repo: RefreshTokenRepository,
        token_service: TokenService,
        org_member_repo: OrganizationMemberRepository,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo
        self._token_service = token_service
        self._org_member_repo = org_member_repo

    @transactional
    async def refresh(self, raw_refresh_token: str) -> AuthTokenPair:
        """
        Exchange a valid refresh token for a new access + refresh token pair.

        Implements refresh token rotation: the provided token is revoked
        immediately after use and a new one is issued and persisted.

        Steps:
            1. Verify JWT signature and type of the refresh token.
            2. Look up the token hash in DB (must exist, not revoked, not expired).
            3. Verify user account status.
            4. Revoke the old refresh token record (rotation).
            5. Issue a new token pair with updated user claims and roles.
            6. Persist the new refresh token hash.

        Returns:
            New AuthTokenPair.

        Raises:
            InvalidRefreshTokenError: for any invalid/expired/revoked token or inactive account.
        """
        # 1. Verify JWT signature and type claim
        user_id = self._token_service.verify_refresh_token(raw_refresh_token)

        # 2. Look up the token hash in DB
        token_hash = self._token_service.hash_token(raw_refresh_token)
        stored_token = await self._refresh_token_repo.find_by_token_hash(token_hash)
        if stored_token is None:
            raise InvalidRefreshTokenError(
                "Refresh token not found, already used, or expired."
            )

        # 3. Verify user is active
        user = await self._user_repo.find_by_id(user_id)
        if user is None or user.status != AppUserStatus.ACTIVE:
            raise InvalidRefreshTokenError("User account is inactive or not found.")

        # 4. Revoke old token (rotation)
        await self._revoke_token_record(stored_token)

        # 5. Look up roles
        roles = await self._org_member_repo.find_roles_by_user(user.id)
        token_roles = roles if roles else None

        # 6. Issue new pair
        new_token_pair = self._token_service.issue_pair(
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=token_roles,
        )

        # 7. Persist new refresh token
        await self._persist_refresh_token(user.id, new_token_pair.refresh_token)

        return new_token_pair

    @transactional
    async def revoke(self, raw_refresh_token: str, requesting_user_id: int) -> None:
        """
        Revoke a refresh token (logout).

        This operation is idempotent: if the token is not found or is already
        revoked, it silently succeeds rather than raising an error.

        Steps:
            1. Hash the raw token and look it up in DB.
            2. Verify ownership — token must belong to requesting_user_id.
            3. Mark as revoked.

        Raises:
            InvalidRefreshTokenError: if the token belongs to a different user.
        """
        token_hash = self._token_service.hash_token(raw_refresh_token)

        # Look up without active-only filter to detect ownership mismatch
        # even on already-revoked tokens
        stored_token = await self._refresh_token_repo.find_by_token_hash_any(token_hash)
        if stored_token is None:
            # Token not found or already expired — treat as idempotent success
            return

        if stored_token.user_id != requesting_user_id:
            raise InvalidRefreshTokenError(
                "Refresh token does not belong to the current user."
            )

        if not stored_token.is_revoked:
            await self._revoke_token_record(stored_token)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _revoke_token_record(self, token: RefreshToken) -> None:
        token.is_revoked = True
        token.revoked_at = datetime.now(UTC)
        await self._refresh_token_repo.save_and_flush(token)

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
