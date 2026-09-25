"""Organization domain GraphQL output types."""
from datetime import datetime

import strawberry
from strawberry.types import Info

from app.graphql.organization import enums  # noqa: F401 - ensures GraphQL enum registration
from app.graphql.user.types import UserType
from app.model.identity.organization import OrgStatus


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
