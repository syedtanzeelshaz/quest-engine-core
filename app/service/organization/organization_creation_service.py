"""Organization creation domain service."""
from app.core.transaction import transactional
from app.graphql.organization.inputs import CreateOrganizationInput
from app.model.identity.organization import Organization, OrgStatus
from app.model.identity.organization_member import (
    OrganizationMember,
    OrgMemberStatus,
)
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.repository.identity.organization_repo import OrganizationRepository
from app.repository.identity.role_repo import RoleRepository
from app.service.organization.organization_validator import OrganizationValidator
from app.service.user.models import AdminRole
from app.util.logger import log


class OrganizationCreationService:
    """Domain service handling tenant organization creation and initial membership setup."""

    def __init__(
        self,
        org_repo: OrganizationRepository,
        org_member_repo: OrganizationMemberRepository,
        role_repo: RoleRepository,
        org_validator: OrganizationValidator,
    ) -> None:
        self._org_repo = org_repo
        self._org_member_repo = org_member_repo
        self._role_repo = role_repo
        self._org_validator = org_validator

    @transactional
    async def create(
        self,
        user_id: int,
        input_data: CreateOrganizationInput,
    ) -> Organization:
        """
        Create a new tenant organization and assign the creator as SUPER_ADMIN.

        Raises:
            SlugAlreadyExistsError: If the provided slug is already taken.
            RuntimeError: If the required system role is missing from the database.
        """
        log.info("[create] Creating organization name=%s, slug=%s for user_id=%s", input_data.name, input_data.slug, user_id)

        await self._org_validator.validate_slug_availability(input_data.slug)

        org = Organization(
            name=input_data.name,
            slug=input_data.slug,
            description=input_data.description,
            status=OrgStatus.ACTIVE,
        )
        created_org = await self._org_repo.save_and_flush(org)

        super_admin_role = await self._role_repo.find_by_name(AdminRole.SUPER_ADMIN.value)
        if super_admin_role is None:
            log.error("[create] Required role '%s' not found in database", AdminRole.SUPER_ADMIN.value)
            raise RuntimeError(
                f"Required role '{AdminRole.SUPER_ADMIN.value}' is not configured in the system."
            )

        membership = OrganizationMember(
            user_id=user_id,
            org_id=created_org.id,
            role_id=super_admin_role.id,
            status=OrgMemberStatus.ACTIVE,
        )
        await self._org_member_repo.save_and_flush(membership)

        log.info("[create] Created organization id=%s with creator user_id=%s as SUPER_ADMIN", created_org.id, user_id)

        return created_org
