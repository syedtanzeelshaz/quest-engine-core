from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.organization import Organization, OrgStatus
from app.repository.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Data access repository for identity.organization."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    async def find_by_slug(self, slug: str) -> Organization | None:
        """Fetch an organization by its unique URL slug."""
        stmt = select(Organization).where(Organization.slug == slug).limit(1)
        return await self.session.scalar(stmt)

    async def exists_by_slug(self, slug: str) -> bool:
        """Check whether an organization with the given slug exists."""
        stmt = (
            select(1)
            .select_from(Organization)
            .where(Organization.slug == slug)
            .limit(1)
        )
        return (await self.session.scalar(stmt)) is not None

    async def find_all_by_status_in(
        self,
        statuses: Sequence[OrgStatus],
    ) -> list[Organization]:
        """Fetch organizations matching a sequence of statuses."""
        if not statuses:
            return []
        stmt = select(Organization).where(Organization.status.in_(statuses))
        res = await self.session.scalars(stmt)
        return list(res.all())
