from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.identity.organization import Organization, OrgStatus
from app.repository.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Data access repository for identity.organization."""

    def __init__(self, session: Session) -> None:
        super().__init__(Organization, session)

    def find_by_slug(self, slug: str) -> Organization | None:
        """Fetch an organization by its unique URL slug."""
        stmt = select(Organization).where(Organization.slug == slug)
        return self.session.scalar(stmt)

    def exists_by_slug(self, slug: str) -> bool:
        """Check whether an organization with the given slug exists."""
        stmt = select(1).select_from(Organization).where(Organization.slug == slug).limit(1)
        return self.session.scalar(stmt) is not None

    def find_all_by_status_in(
        self,
        statuses: Sequence[OrgStatus],
        skip: int = 0,
        limit: int = 100,
    ) -> list[Organization]:
        """Fetch organizations matching a sequence of statuses."""
        if not statuses:
            return []
        stmt = (
            select(Organization)
            .where(Organization.status.in_(statuses))
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
