from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.agent import Agent
from app.repository.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Data access repository for tenant.agent."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Agent, session)

