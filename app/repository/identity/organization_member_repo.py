from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.organization_member import OrganizationMember, OrgMemberStatus
from app.model.identity.role import Role
from app.repository.base import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """Data access repository for identity.organization_member."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(OrganizationMember, session)

    async def find_all_by_user_and_org(
        self,
        user_id: int,
        org_id: int,
    ) -> list[OrganizationMember]:
        """Fetch all membership records for a specific user and organization."""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.org_id == org_id,
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_active_by_user(self, user_id: int) -> list[OrganizationMember]:
        """Fetch all active organization memberships for a user."""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == OrgMemberStatus.ACTIVE,
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_by_org(self, org_id: int) -> list[OrganizationMember]:
        """Fetch all member records for an organization."""
        stmt = select(OrganizationMember).where(OrganizationMember.org_id == org_id)
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_roles_by_user(self, user_id: int) -> list[str]:
        """Fetch unique active role names assigned to a user across organizations."""
        stmt = (
            select(Role.name)
            .join(OrganizationMember, OrganizationMember.role_id == Role.id)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.status == OrgMemberStatus.ACTIVE,
            )
            .distinct()
        )
        res = await self.session.scalars(stmt)
        return list(res.all())
