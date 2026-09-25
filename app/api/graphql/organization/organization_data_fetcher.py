"""Organization domain GraphQL query fetchers."""
import strawberry
from strawberry.types import Info

from app.core.constants import OrganizationMessage
from app.graphql.common.context import GraphQLContext
from app.graphql.common.permissions import IsAuthenticated
from app.graphql.organization import mappers
from app.graphql.organization.types import OrganizationType
from app.repository.identity.organization_repo import OrganizationRepository
from app.service.organization.organization_query_service import (
    OrganizationQueryService,
)
from app.util.logger import log


@strawberry.type
class OrganizationDataFetcher:
    """Organization domain query operations."""

    @strawberry.field(
        description="Retrieve organization details by id, slug, or default to caller's active organization.",
        permission_classes=[IsAuthenticated],
    )
    async def organization(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.ID | None = None,
        slug: str | None = None,
    ) -> OrganizationType:
        current_user = info.context.require_user()
        log.info("[organization] Fetching organization query (id=%s, slug=%s) by caller user_id=%s", id, slug, current_user.id)

        org_repo = OrganizationRepository(info.context.db)
        org_query_service = OrganizationQueryService(org_repo=org_repo)

        org = None
        if id is not None:
            try:
                org = await org_query_service.get_by_id(int(id))
            except ValueError:
                log.warning("[organization] Invalid id format: %s", id)
                raise Exception(OrganizationMessage.ORGANIZATION_NOT_FOUND)
        elif slug is not None:
            org = await org_query_service.get_by_slug(slug)
        else:
            current_user = info.context.require_org_member()
            org = await org_query_service.get_by_id(current_user.org_id)

        if org is None:
            log.warning("[organization] Organization not found (id=%s, slug=%s)", id, slug)
            raise Exception(OrganizationMessage.ORGANIZATION_NOT_FOUND)

        return mappers.organization_to_type(org)
