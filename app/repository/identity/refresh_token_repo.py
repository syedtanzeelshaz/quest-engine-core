from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.refresh_token import RefreshToken
from app.repository.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Data access repository for identity.refresh_token."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def find_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Fetch an active (non-revoked, non-expired) refresh token by its SHA-256 hash."""
        now = datetime.now(UTC)
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
                RefreshToken.expires_at > now,
            )
            .limit(1)
        )
        return await self.session.scalar(stmt)

    async def find_by_token_hash_any(self, token_hash: str) -> RefreshToken | None:
        """
        Fetch a refresh token by hash regardless of revocation or expiry status.
        Used for ownership verification during logout.
        """
        stmt = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .limit(1)
        )
        return await self.session.scalar(stmt)

    async def find_all_active_by_user(self, user_id: int) -> list[RefreshToken]:
        """Fetch all active (non-revoked, non-expired) refresh tokens for a user."""
        now = datetime.now(UTC)
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def revoke_all_by_user(self, user_id: int) -> int:
        """
        Revoke all active refresh tokens for a user (logout from all devices).
        Returns the count of tokens revoked.
        """
        now = datetime.now(UTC)
        tokens = await self.find_all_active_by_user(user_id)
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = now
        if tokens:
            await self.session.flush()
        return len(tokens)
