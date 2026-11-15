from questengine.registry.types import MemberStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.member import Member
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
