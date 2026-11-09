from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.operator import Operator, OperatorStatus
from app.model.identity.operator_role import OperatorRole
from app.model.identity.role import Role
from app.repository.base import BaseRepository


class OperatorRepository(BaseRepository[Operator]):
    """Data access repository for identity.operator."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        super().__init__(Operator, session)


    async def find_by_user_id(self, user_id: int) -> Operator | None:
        """Fetch an operator persona by their app_user id."""
        stmt = select(Operator).where(Operator.user_id == user_id).limit(1)
        return await self.session.scalar(stmt)


    async def find_by_corporate_email(self, corporate_email: str) -> Operator | None:
        """Fetch an operator persona by corporate email."""
        stmt = select(Operator).where(Operator.corporate_email == corporate_email).limit(1)
        return await self.session.scalar(stmt)


    async def find_roles_by_user_id(self, user_id: int) -> list[str]:
        """Fetch active operations role names assigned to an operator."""
        stmt = (
            select(Role.name)
            .join(OperatorRole, OperatorRole.role_id == Role.id)
            .join(Operator, Operator.id == OperatorRole.operator_id)
            .where(
                Operator.user_id == user_id,
                Operator.status == OperatorStatus.ACTIVE,
            )
            .distinct()
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

