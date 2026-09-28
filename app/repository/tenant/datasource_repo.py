from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.datasource import Datasource
from app.repository.base import BaseRepository


class DatasourceRepository(BaseRepository[Datasource]):
    """Data access repository for tenant.datasource."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Datasource, session)

    async def find_all_by_org(self, org_id: int) -> list[Datasource]:
        """Fetch all datasources belonging to an organization."""
        stmt = select(Datasource).where(Datasource.org_id == org_id)
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_by_org_ids(self, org_ids: Sequence[int]) -> dict[int, list[Datasource]]:
        """Fetch all datasources belonging to the specified organization IDs, grouped by org_id."""
        if not org_ids:
            return {}
        stmt = select(Datasource).where(Datasource.org_id.in_(org_ids))
        res = await self.session.scalars(stmt)
        result: dict[int, list[Datasource]] = {org_id: [] for org_id in org_ids}
        for ds in res.all():
            result[ds.org_id].append(ds)
        return result

