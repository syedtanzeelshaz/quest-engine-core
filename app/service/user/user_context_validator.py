"""
UserContextValidator — identity, tenancy, and role validation for caller contexts.

Guards request contexts against missing authentication, missing organization tenancy,
or insufficient administrator privileges.
"""
from app.core.constants import SecurityMessage
from app.core.exceptions import (
    AccessDeniedError,
    AuthenticationRequiredError,
    OrganizationRequiredError,
)
from app.service.user.models import AdminRole, CurrentUser
from app.util.logger import log


class UserContextValidator:
    """Validates identity, membership, and authorization constraints on caller contexts."""

    def __init__(self) -> None:
        pass

    def require_authenticated_user(self, user: CurrentUser | None) -> CurrentUser:
        """
        Verify that a caller context is authenticated.
        Returns the non-null CurrentUser or raises AuthenticationRequiredError.
        """
        if user is None:
            log.warning("[UserContextValidator] Access denied: unauthenticated caller context")
            raise AuthenticationRequiredError(SecurityMessage.AUTHENTICATION_REQUIRED)
        return user

    def require_org_member(self, user: CurrentUser | None) -> CurrentUser:
        """
        Verify that caller is authenticated and belongs to an active organization.
        Returns the non-null CurrentUser or raises OrganizationRequiredError.
        """
        current_user = self.require_authenticated_user(user)
        if current_user.org_id is None:
            log.warning("[UserContextValidator] Access denied: user_id=%s missing organization membership", current_user.id)
            raise OrganizationRequiredError(SecurityMessage.ORGANIZATION_MEMBERSHIP_REQUIRED)
        return current_user

    def require_org_admin(self, user: CurrentUser | None) -> CurrentUser:
        """
        Verify that caller has organization administrator or super admin privileges.
        Returns the non-null CurrentUser or raises AccessDeniedError.
        """
        current_user = self.require_org_member(user)
        admin_roles = {AdminRole.SUPER_ADMIN, AdminRole.ADMIN}
        if not any(role in admin_roles for role in current_user.roles):
            log.warning(
                "[UserContextValidator] Access denied: user_id=%s has roles=%s, requires admin privileges",
                current_user.id,
                current_user.roles,
            )
            raise AccessDeniedError(SecurityMessage.ADMIN_ACCESS_REQUIRED)
        return current_user

