from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.agent_datasource import AgentDatasource
from app.repository.base import BaseRepository


class AgentDatasourceRepository(BaseRepository[AgentDatasource]):
    """Data access repository for tenant.agent_datasource associations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentDatasource, session)

