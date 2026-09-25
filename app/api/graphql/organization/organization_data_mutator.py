"""Organization domain GraphQL mutation resolvers."""
import strawberry
from strawberry.types import Info

from app.graphql.common.context import GraphQLContext
from app.graphql.common.permissions import IsAuthenticated, IsOrgAdmin
from app.graphql.organization import mappers
from app.graphql.organization.inputs import (
    CreateOrganizationInput,
    UpdateOrganizationInput,
)
from app.graphql.organization.types import OrganizationType
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.repository.identity.organization_repo import OrganizationRepository
from app.repository.identity.role_repo import RoleRepository
from app.service.organization.organization_creation_service import (
    OrganizationCreationService,
)
from app.service.organization.organization_update_service import (
    OrganizationUpdateService,
)
from app.service.organization.organization_validator import (
    OrganizationValidator,
)
from app.util.logger import log


@strawberry.type
class OrganizationDataMutator:
    """Organization domain mutation operations."""

    @strawberry.mutation(
        description="Create a new tenant organization and assign caller as super admin.",
        permission_classes=[IsAuthenticated],
    )
    async def create_organization(
        self,
        info: Info[GraphQLContext, None],
        input: CreateOrganizationInput,
    ) -> OrganizationType:
        ctx = info.context
        current_user = ctx.require_user()
        log.info("[create_organization] Mutation received: user_id=%s, name=%s, slug=%s", current_user.id, input.name, input.slug)

        org_repo = OrganizationRepository(ctx.db)
        org_member_repo = OrganizationMemberRepository(ctx.db)
        role_repo = RoleRepository(ctx.db)
        org_validator = OrganizationValidator(org_repo)
        org_creation_service = OrganizationCreationService(
            org_repo=org_repo,
            org_member_repo=org_member_repo,
            role_repo=role_repo,
            org_validator=org_validator,
        )

        created_org = await org_creation_service.create(
            user_id=current_user.id,
            input_data=input,
        )

        return mappers.organization_to_type(created_org)

    @strawberry.mutation(
        description="Update organization details (requires organization admin privileges).",
        permission_classes=[IsAuthenticated, IsOrgAdmin],
    )
    async def update_organization(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.ID,
        input: UpdateOrganizationInput,
    ) -> OrganizationType:
        ctx = info.context
        current_user = ctx.require_org_admin()
        log.info("[update_organization] Mutation received: org_id=%s by admin user_id=%s", id, current_user.id)

        org_repo = OrganizationRepository(ctx.db)
        org_update_service = OrganizationUpdateService(org_repo=org_repo)

        updated_org = await org_update_service.update(
            org_id=int(id),
            input_data=input,
        )

        return mappers.organization_to_type(updated_org)
