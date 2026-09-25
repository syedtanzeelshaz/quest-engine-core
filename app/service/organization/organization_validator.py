"""Organization domain validator."""
from app.core.constants import OrganizationMessage
from app.core.exceptions import SlugAlreadyExistsError
from app.repository.identity.organization_repo import OrganizationRepository
from app.util.logger import log


class OrganizationValidator:
    """Validates organization existence and business invariants."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        self._org_repo = org_repo


    async def validate_slug_availability(self, slug: str) -> None:
        """
        Ensure the slug is not already taken by an existing organization.

        Raises:
            SlugAlreadyExistsError: If the slug already exists.
        """
        if await self._org_repo.exists_by_slug(slug):
            log.warning("[validate_slug_availability] Organization slug '%s' is already in use", slug)
            raise SlugAlreadyExistsError(OrganizationMessage.SLUG_ALREADY_EXISTS)
