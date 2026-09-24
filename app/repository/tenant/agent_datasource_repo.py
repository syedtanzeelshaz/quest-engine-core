from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.agent_datasource import AgentDatasource
from app.repository.base import BaseRepository


class AgentDatasourceRepository(BaseRepository[AgentDatasource]):
    """Data access repository for tenant.agent_datasource associations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentDatasource, session)

    async def find_by_agent_and_datasource(
        self,
        agent_id: int,
        datasource_id: int,
    ) -> AgentDatasource | None:
        """Fetch an association between an agent and a datasource."""
        stmt = (
            select(AgentDatasource)
            .where(
                AgentDatasource.agent_id == agent_id,
                AgentDatasource.datasource_id == datasource_id,
            )
            .limit(1)
        )
        return await self.session.scalar(stmt)

    async def find_all_by_agent(self, agent_id: int) -> list[AgentDatasource]:
        """Fetch all datasource associations for an agent."""
        stmt = select(AgentDatasource).where(AgentDatasource.agent_id == agent_id)
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_by_datasource(self, datasource_id: int) -> list[AgentDatasource]:
        """Fetch all agent associations for a datasource."""
        stmt = select(AgentDatasource).where(
            AgentDatasource.datasource_id == datasource_id
        )
        res = await self.session.scalars(stmt)
        return list(res.all())
