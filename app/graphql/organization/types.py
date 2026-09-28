"""Organization domain GraphQL output types."""
from datetime import datetime

import strawberry
from strawberry.types import Info

from app.graphql.datasource.types import DatasourceType
from app.graphql.organization.enums import OrgStatus
from app.graphql.user.types import UserType


@strawberry.type(name="Organization", description="Tenant organization representation.")
class OrganizationType:
    id: strawberry.ID
    name: str
    slug: str
    description: str | None = None
    status: OrgStatus | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @strawberry.field(description="Active members belonging to this organization.")
    async def users(self, info: Info) -> list[UserType]:
        return await info.context.loaders.users_by_org_id.load(int(self.id))

    @strawberry.field(description="Datasources connected to this organization.")
    async def datasources(self, info: Info) -> list[DatasourceType]:
        return await info.context.loaders.datasources_by_org_id.load(int(self.id))

