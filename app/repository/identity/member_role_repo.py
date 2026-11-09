from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.member_role import MemberRole
from app.repository.base import BaseRepository


class MemberRoleRepository(BaseRepository[MemberRole]):
    """Data access repository for identity.member_role."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(MemberRole, session)

