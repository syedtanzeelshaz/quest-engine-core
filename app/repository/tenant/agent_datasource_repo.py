from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.tenant.agent_datasource import AgentDatasource
from app.repository.base import BaseRepository


class AgentDatasourceRepository(BaseRepository[AgentDatasource]):
    """Data access repository for tenant.agent_datasource associations."""

    def __init__(self, session: Session) -> None:
        super().__init__(AgentDatasource, session)

    def find_by_agent_and_datasource(
        self,
        agent_id: int,
        datasource_id: int,
        org_id: int,
    ) -> AgentDatasource | None:
        """Fetch an association between an agent and a datasource within an organization."""
        stmt = select(AgentDatasource).where(
            AgentDatasource.agent_id == agent_id,
            AgentDatasource.datasource_id == datasource_id,
            AgentDatasource.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def find_all_by_agent(self, agent_id: int, org_id: int) -> list[AgentDatasource]:
        """Fetch all datasource associations for an agent."""
        stmt = select(AgentDatasource).where(
            AgentDatasource.agent_id == agent_id,
            AgentDatasource.org_id == org_id,
        )
        return list(self.session.scalars(stmt).all())

    def find_all_by_datasource(self, datasource_id: int, org_id: int) -> list[AgentDatasource]:
        """Fetch all agent associations for a datasource."""
        stmt = select(AgentDatasource).where(
            AgentDatasource.datasource_id == datasource_id,
            AgentDatasource.org_id == org_id,
        )
        return list(self.session.scalars(stmt).all())
