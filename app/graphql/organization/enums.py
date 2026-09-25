"""Organization domain GraphQL enums."""
import strawberry

from app.model.identity.organization import OrgStatus
from app.model.identity.organization_member import OrgMemberStatus

OrgStatus = strawberry.enum(
    OrgStatus,
    name="OrgStatus",
    description="Tenant organization lifecycle status.",
)

OrgMemberStatus = strawberry.enum(
    OrgMemberStatus,
    name="OrgMemberStatus",
    description="Membership status of a user within an organization.",
)

__all__ = [
    "OrgMemberStatus",
    "OrgStatus",
]
