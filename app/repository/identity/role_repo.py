"""
Role repository and permission resolution queries.
"""
from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
