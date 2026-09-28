"""Datasource query domain service."""
from collections.abc import Sequence

from app.model.tenant.datasource import Datasource
from app.repository.tenant.datasource_repo import DatasourceRepository
from app.util.logger import log


class DatasourceQueryService:
    """Domain service handling datasource read/query operations."""

    def __init__(self, datasource_repo: DatasourceRepository) -> None:
        self._datasource_repo = datasource_repo

    async def get_by_id(self, datasource_id: int) -> Datasource | None:
        """Fetch a datasource by its primary key ID."""
        log.info("[get_by_id] Fetching datasource for datasource_id=%s", datasource_id)
        return await self._datasource_repo.find_by_id(datasource_id)

    async def get_by_ids(self, datasource_ids: Sequence[int]) -> list[Datasource]:
        """Fetch datasources matching a sequence of IDs."""
        log.info("[get_by_ids] Batch fetching datasources for %d ID(s)", len(datasource_ids))
        return await self._datasource_repo.find_all_by_ids(datasource_ids)

    async def get_by_org_id(self, org_id: int) -> list[Datasource]:
        """Fetch all datasources for a single organization."""
        log.info("[get_by_org_id] Fetching datasources for org_id=%s", org_id)
        return await self._datasource_repo.find_all_by_org(org_id)

    async def get_by_org_ids(self, org_ids: Sequence[int]) -> dict[int, list[Datasource]]:
        """
        Batch fetch datasources mapped by organization ID.
        Guarantees that every requested org_id exists in the returned dictionary.
        """
        log.info("[get_by_org_ids] Batch fetching datasources for %d org ID(s)", len(org_ids))
        return await self._datasource_repo.find_all_by_org_ids(org_ids)

