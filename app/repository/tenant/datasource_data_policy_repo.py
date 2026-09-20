from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.tenant.datasource_data_policy import DatasourceDataPolicy
from app.repository.base import BaseRepository


class DatasourceDataPolicyRepository(BaseRepository[DatasourceDataPolicy]):
    """Data access repository for tenant.datasource_data_policy."""

    def __init__(self, session: Session) -> None:
        super().__init__(DatasourceDataPolicy, session)

    def find_all_by_datasource(
        self,
        datasource_id: int,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DatasourceDataPolicy]:
        """Fetch all data policies defined for a datasource."""
        stmt = (
            select(DatasourceDataPolicy)
            .where(
                DatasourceDataPolicy.datasource_id == datasource_id,
                DatasourceDataPolicy.org_id == org_id,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
