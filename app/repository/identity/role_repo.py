from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.identity.role import Role
from app.repository.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Data access repository for identity.role."""

    def __init__(self, session: Session) -> None:
        super().__init__(Role, session)

    def find_by_name(self, name: str) -> Role | None:
        """Fetch a role by its unique name (e.g. SUPER_ADMIN, ADMIN, MEMBER)."""
        stmt = select(Role).where(Role.name == name)
        return self.session.scalar(stmt)

    def exists_by_name(self, name: str) -> bool:
        """Check whether a role with the given name exists."""
        stmt = select(1).select_from(Role).where(Role.name == name).limit(1)
        return self.session.scalar(stmt) is not None
