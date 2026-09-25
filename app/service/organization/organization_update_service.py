"""Organization update domain service."""
from app.core.exceptions import OrganizationNotFoundError
from app.core.transaction import transactional
from app.graphql.organization.inputs import UpdateOrganizationInput
from app.model.identity.organization import Organization
from app.repository.identity.organization_repo import OrganizationRepository
from app.util.logger import log


class OrganizationUpdateService:
    """Domain service handling organization profile and attribute updates."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        self._org_repo = org_repo

    @transactional
    async def update(
        self,
        org_id: int,
        input_data: UpdateOrganizationInput,
    ) -> Organization:
        """
        Update mutable attributes for an organization.

        Raises:
            OrganizationNotFoundError: If no organization with the given ID exists.
        """
        log.info("[update] Updating organization for org_id=%s, with input=%s", org_id, input_data)

        org = await self._org_repo.find_by_id(org_id)
        if org is None:
            log.warning("[update] Organization with org_id=%s not found", org_id)
            raise OrganizationNotFoundError(f"Organization with ID {org_id} not found.")

        if input_data.name is not None:
            org.name = input_data.name
        if input_data.description is not None:
            org.description = input_data.description

        updated_org = await self._org_repo.save_and_flush(org)
        log.info("[update] Updated organization for org_id=%s successfully", org_id)

        return updated_org
