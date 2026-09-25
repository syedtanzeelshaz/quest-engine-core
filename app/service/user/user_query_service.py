"""User query domain service."""
from collections.abc import Sequence

from app.model.identity.app_user import AppUser
from app.repository.identity.app_user_repo import AppUserRepository
from app.util.logger import log


class UserQueryService:
    """Domain service handling user read/query operations."""

    def __init__(self, user_repo: AppUserRepository) -> None:
        self._user_repo = user_repo


    async def get_by_id(self, user_id: int) -> AppUser | None:
        """Fetch an application user by their primary key ID."""
        log.info("[get_by_id] Fetching user for user_id=%s", user_id)
        return await self._user_repo.find_by_id(user_id)


    async def get_by_ids(self, user_ids: Sequence[int]) -> list[AppUser]:
        """Fetch users matching a sequence of IDs."""
        log.info("[get_by_ids] Batch fetching users for %d ID(s)", len(user_ids))
        return await self._user_repo.find_all_by_ids(user_ids)
