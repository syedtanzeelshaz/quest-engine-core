from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.agent_access_policy import AgentAccessPolicy
from app.repository.base import BaseRepository


class AgentAccessPolicyRepository(BaseRepository[AgentAccessPolicy]):
    """Data access repository for tenant.agent_access_policy."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentAccessPolicy, session)

    async def find_all_by_agent(self, agent_id: int) -> list[AgentAccessPolicy]:
        """Fetch all access policies defined for an agent."""
        stmt = select(AgentAccessPolicy).where(AgentAccessPolicy.agent_id == agent_id)
        res = await self.session.scalars(stmt)
        return list(res.all())
