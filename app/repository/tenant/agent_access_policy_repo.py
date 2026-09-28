from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.agent_access_policy import AgentAccessPolicy
from app.repository.base import BaseRepository


class AgentAccessPolicyRepository(BaseRepository[AgentAccessPolicy]):
    """Data access repository for tenant.agent_access_policy."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentAccessPolicy, session)

