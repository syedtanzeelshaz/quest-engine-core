"""
GraphQL permission classes.

Evaluated by Strawberry on field and mutation resolvers before execution.
Failures return structured GraphQL errors without failing HTTP status.
"""
from strawberry.permission import BasePermission
from strawberry.types import Info

from app.graphql.common.constants import GraphQLMessage
from app.graphql.common.context import GraphQLContext
from app.service.user.models import AdminRole


class IsAuthenticated(BasePermission):
    """Requires the request to have a valid authenticated CurrentUser."""
    message = GraphQLMessage.AUTHENTICATION_REQUIRED

    def has_permission(self, source: object, info: Info[GraphQLContext, None], **kwargs) -> bool:
        return info.context.current_user is not None


class IsOrgMember(BasePermission):
    """Requires the authenticated user to be an active member of an organization."""
    message = GraphQLMessage.ORGANIZATION_MEMBERSHIP_REQUIRED

    def has_permission(self, source: object, info: Info[GraphQLContext, None], **kwargs) -> bool:
        user = info.context.current_user
        return user is not None and user.org_id is not None


class IsOrgAdmin(BasePermission):
    """Requires the authenticated user to have admin or super admin privileges."""
    message = GraphQLMessage.ADMIN_ACCESS_REQUIRED

    def has_permission(self, source: object, info: Info[GraphQLContext, None], **kwargs) -> bool:
        user = info.context.current_user
        if user is None or user.org_id is None:
            return False
        admin_roles = {AdminRole.SUPER_ADMIN, AdminRole.ADMIN}
        return any(role in admin_roles for role in user.roles)

