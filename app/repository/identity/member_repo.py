from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.member import Member, MemberStatus
from app.model.identity.member_role import MemberRole
from app.model.identity.role import Role
from app.repository.base import BaseRepository


class MemberRepository(BaseRepository[Member]):
    """Data access repository for identity.member."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(Member, session)


    async def find_by_user_id(self, user_id: int) -> Member | None:
        """Fetch a member persona by the underlying auth app_user id."""
        stmt = select(Member).where(Member.user_id == user_id).limit(1)
        return await self.session.scalar(stmt)


    async def find_by_email_and_org(self, org_id: int, email: str) -> Member | None:
        """Fetch a member by email within a specific organization."""
        stmt = select(Member).where(
            Member.org_id == org_id,
            Member.email == email,
        ).limit(1)
        return await self.session.scalar(stmt)


    async def find_all_active_by_org(self, org_id: int) -> list[Member]:
        """Fetch all active members of an organization."""
        stmt = select(Member).where(
            Member.org_id == org_id,
            Member.status == MemberStatus.ORG_ACTIVE,
        )
        res = await self.session.scalars(stmt)
        return list(res.all())


    async def find_roles_by_user_id(self, user_id: int) -> list[str]:
        """Fetch active role names assigned to a member across their current organization."""
        stmt = (
            select(Role.name)
            .join(MemberRole, MemberRole.role_id == Role.id)
            .join(Member, Member.id == MemberRole.member_id)
            .where(
                Member.user_id == user_id,
                Member.status == MemberStatus.ORG_ACTIVE,
            )
            .distinct()
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

