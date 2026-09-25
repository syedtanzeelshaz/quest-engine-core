"""Organization query domain service."""
from collections.abc import Sequence

from app.model.identity.app_user import AppUser
from app.model.identity.organization import Organization
from app.repository.identity.organization_repo import OrganizationRepository
from app.util.logger import log


class OrganizationQueryService:
    """Domain service handling organization read/query operations."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        self._org_repo = org_repo


    async def get_by_id(self, org_id: int) -> Organization | None:
        """Fetch an organization by its primary key ID."""
        log.info("[get_by_id] Fetching organization for org_id=%s", org_id)
        return await self._org_repo.find_by_id(org_id)


    async def get_by_slug(self, slug: str) -> Organization | None:
        """Fetch an organization by its unique URL slug."""
        log.info("[get_by_slug] Fetching organization for slug=%s", slug)
        return await self._org_repo.find_by_slug(slug)


    async def get_by_ids(self, org_ids: Sequence[int]) -> list[Organization]:
        """Fetch organizations matching a sequence of IDs."""
        log.info("[get_by_ids] Batch fetching organizations for %d ID(s)", len(org_ids))
        return await self._org_repo.find_all_by_ids(org_ids)


    async def get_active_users_by_org_ids(
        self,
        org_ids: Sequence[int],
    ) -> Sequence[tuple[int, AppUser]]:
        """Fetch active users mapped to organization IDs."""
        log.info("[get_active_users_by_org_ids] Fetching active users for %d organization(s)", len(org_ids))
        return await self._org_repo.find_active_users_by_org_ids(org_ids)
