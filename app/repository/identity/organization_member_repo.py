from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.identity.organization_member import OrganizationMember, OrgMemberStatus
from app.repository.base import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """Data access repository for identity.organization_member."""

    def __init__(self, session: Session) -> None:
        super().__init__(OrganizationMember, session)

    def find_by_user_and_org(self, user_id: int, org_id: int) -> OrganizationMember | None:
        """Fetch a membership record for a specific user and organization."""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def find_active_membership(self, user_id: int) -> OrganizationMember | None:
        """Fetch the single active organization membership for a user."""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == OrgMemberStatus.ACTIVE,
        )
        return self.session.scalar(stmt)

    def find_all_by_org(
        self,
        org_id: int,
        status: OrgMemberStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[OrganizationMember]:
        """Fetch all member records for an organization, optionally filtered by status."""
        stmt = select(OrganizationMember).where(OrganizationMember.org_id == org_id)
        if status is not None:
            stmt = stmt.where(OrganizationMember.status == status)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())
