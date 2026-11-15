"""
Role repository and permission resolution queries.
"""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.member_role import MemberRole
from app.model.identity.permission import Permission
from app.model.identity.role import Role
from app.model.identity.role_permission import RolePermission
from app.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Data access repository for identity.role."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(Role, session)


    async def find_by_name(self, name: str) -> Role | None:
        """Fetch a role by its unique name (e.g. SUPER_ADMIN, ADMIN, STAFF)."""
        stmt = select(Role).where(Role.name == name).limit(1)
        return await self.session.scalar(stmt)


    async def find_roles_by_member_id(self, member_id: int) -> list[Role]:
        """Fetch all roles assigned to a member."""
        stmt = (
            select(Role)
            .join(MemberRole, MemberRole.role_id == Role.id)
            .where(MemberRole.member_id == member_id)
        )
        res = await self.session.scalars(stmt)
        return list(res.all())


    async def find_roles_by_member_ids(self, member_ids: Sequence[int]) -> dict[int, list[Role]]:
        """Batch-fetch roles grouped by member_id to eliminate N+1 queries."""
        if not member_ids:
            return {}
        stmt = (
            select(MemberRole.member_id, Role)
            .join(Role, Role.id == MemberRole.role_id)
            .where(MemberRole.member_id.in_(member_ids))
        )
        res = await self.session.execute(stmt)
        mapping: dict[int, list[Role]] = {mid: [] for mid in member_ids}
        for mid, role in res.all():
            mapping[mid].append(role)
        return mapping


    async def find_permissions_by_roles(self, role_names: Sequence[str], experience: str) -> set[str]:
        """Fetch all distinct permission strings assigned to the specified roles for an experience context."""
        if not role_names:
            return set()

        stmt = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                Role.name.in_(role_names),
                Role.experience == experience,
            )
            .distinct()
        )
        res = await self.session.scalars(stmt)
        return set(res.all())
