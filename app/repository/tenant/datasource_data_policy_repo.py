from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.datasource_data_policy import DatasourceDataPolicy
from app.repository.base import BaseRepository


class DatasourceDataPolicyRepository(BaseRepository[DatasourceDataPolicy]):
    """Data access repository for tenant.datasource_data_policy."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DatasourceDataPolicy, session)

