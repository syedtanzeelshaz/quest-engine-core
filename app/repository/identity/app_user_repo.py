from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.app_user import AppUser, AppUserStatus
from app.repository.base import BaseRepository


class AppUserRepository(BaseRepository[AppUser]):
    """Data access repository for identity.app_user."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AppUser, session)

    async def find_by_email(self, email: str) -> AppUser | None:
        """Fetch a user by their unique email address."""
        stmt = select(AppUser).where(AppUser.email == email).limit(1)
        return await self.session.scalar(stmt)

    async def exists_by_email(self, email: str) -> bool:
        """Check whether a user with the given email exists."""
        stmt = select(1).select_from(AppUser).where(AppUser.email == email).limit(1)
        return (await self.session.scalar(stmt)) is not None

    async def find_all_by_status_in(
        self,
        statuses: Sequence[AppUserStatus],
    ) -> list[AppUser]:
        """Fetch users whose status is within the specified collection."""
        if not statuses:
            return []
        stmt = select(AppUser).where(AppUser.status.in_(statuses))
        res = await self.session.scalars(stmt)
        return list(res.all())
