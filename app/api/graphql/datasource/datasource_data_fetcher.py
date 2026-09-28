"""Datasource domain GraphQL query fetchers."""
import strawberry
from strawberry.types import Info

from app.core.primitives.constants import DatasourceMessage
from app.graphql.common.context import GraphQLContext
from app.graphql.common.permissions import IsOrgMember
from app.graphql.datasource import mappers
from app.graphql.datasource.types import DatasourceType
from app.repository.tenant.datasource_repo import DatasourceRepository
from app.service.datasource.datasource_query_service import (
    DatasourceQueryService,
)
from app.util.logger import log


@strawberry.type
class DatasourceDataFetcher:
    """Datasource domain query operations."""

    @strawberry.field(
        description="Retrieve datasource details by id for the caller's organization.",
        permission_classes=[IsOrgMember],
    )
    async def datasource(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.ID,
    ) -> DatasourceType:
        current_user = info.context.require_org_member()
        log.info("[datasource] Fetching datasource (id=%s) for user_id=%s, org_id=%s", id, current_user.id, current_user.org_id)

        try:
            datasource_id = int(id)
        except ValueError:
            log.warning("[datasource] Invalid id format: %s", id)
            raise Exception(DatasourceMessage.DATASOURCE_NOT_FOUND)

        datasource_repo = DatasourceRepository(info.context.db)
        datasource_query_service = DatasourceQueryService(datasource_repo=datasource_repo)

        datasource = await datasource_query_service.get_by_id(datasource_id)
        if datasource is None or datasource.org_id != current_user.org_id:
            log.warning("[datasource] Datasource not found or org mismatch (id=%s, caller_org_id=%s)", id, current_user.org_id)
            raise Exception(DatasourceMessage.DATASOURCE_NOT_FOUND)

        return mappers.datasource_to_type(datasource)

    @strawberry.field(
        description="Retrieve all datasources connected to the caller's organization.",
        permission_classes=[IsOrgMember],
    )
    async def datasources(
        self,
        info: Info[GraphQLContext, None],
    ) -> list[DatasourceType]:
        current_user = info.context.require_org_member()
        log.info("[datasources] Listing datasources for user_id=%s, org_id=%s", current_user.id, current_user.org_id)

        datasource_repo = DatasourceRepository(info.context.db)
        datasource_query_service = DatasourceQueryService(datasource_repo=datasource_repo)

        datasources = await datasource_query_service.get_by_org_id(current_user.org_id)
        return [mappers.datasource_to_type(ds) for ds in datasources]
