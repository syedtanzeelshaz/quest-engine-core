from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.datasource_data_policy import DatasourceDataPolicy
from app.repository.base import BaseRepository


class DatasourceDataPolicyRepository(BaseRepository[DatasourceDataPolicy]):
    """Data access repository for tenant.datasource_data_policy."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DatasourceDataPolicy, session)

    async def find_all_by_datasource(self, datasource_id: int) -> list[DatasourceDataPolicy]:
        """Fetch all data policies defined for a datasource."""
        stmt = select(DatasourceDataPolicy).where(
            DatasourceDataPolicy.datasource_id == datasource_id
        )
        res = await self.session.scalars(stmt)
        return list(res.all())
