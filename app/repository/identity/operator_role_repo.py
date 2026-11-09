from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.operator_role import OperatorRole
from app.repository.base import BaseRepository


class OperatorRoleRepository(BaseRepository[OperatorRole]):
    """Data access repository for identity.operator_role."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(OperatorRole, session)

