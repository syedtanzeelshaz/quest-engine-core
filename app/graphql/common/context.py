"""
GraphQL Context & Request Loader definitions.

Provides per-request state propagation (Database session, CurrentUser, and DataLoaders)
to all GraphQL field resolvers via Strawberry's Info object.
"""
from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from app.api.constants import AUTH_TOKEN_URL
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import InvalidTokenError
from app.graphql.organization.loaders import (
    create_org_users_loader,
    create_organization_loader,
)
from app.graphql.organization.types import OrganizationType
from app.graphql.user.loaders import create_user_loader
from app.graphql.user.types import UserType
from app.model.identity.app_user import AppUserStatus
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.service.authentication.token import TokenService
from app.service.user import CurrentUser, UserContextValidator
from app.util.logger import log

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=AUTH_TOKEN_URL,
    auto_error=False,
)
_token_service = TokenService(settings)
_user_context_validator = UserContextValidator()


@dataclass
class RequestLoaders:
    """
    Per-request DataLoaders container.

    Instantiated once per GraphQL request in get_graphql_context to batch queries
    across nested resolvers and prevent cross-request cache leaks.
    """
    user_by_id: DataLoader[int, UserType | None]
    org_by_id: DataLoader[int, OrganizationType | None]
    users_by_org_id: DataLoader[int, list[UserType]]

    @classmethod
    def create(cls, db: AsyncSession) -> "RequestLoaders":
        return cls(
            user_by_id=create_user_loader(db),
            org_by_id=create_organization_loader(db),
            users_by_org_id=create_org_users_loader(db),
        )


@dataclass
class GraphQLContext(BaseContext):
    """Context object available to every Strawberry resolver via info.context."""
    db: AsyncSession
    loaders: RequestLoaders
    current_user: CurrentUser | None = None

    def require_user(self) -> CurrentUser:
        """
        Return the authenticated CurrentUser.
        Raises AuthenticationRequiredError if caller is not authenticated.
        """
        return _user_context_validator.require_authenticated_user(self.current_user)

    def require_org_member(self) -> CurrentUser:
        """
        Return the authenticated CurrentUser with active organization membership.
        Raises OrganizationRequiredError if caller does not belong to an organization.
        """
        return _user_context_validator.require_org_member(self.current_user)

    def require_org_admin(self) -> CurrentUser:
        """
        Return the authenticated CurrentUser with administrator privileges.
        Raises AccessDeniedError if caller lacks admin roles.
        """
        return _user_context_validator.require_org_admin(self.current_user)



async def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    """
    Extract and verify Bearer token if present, resolving into CurrentUser.
    Returns None if no token was provided or if the token is invalid/expired.
    """
    if not token:
        return None

    try:
        user_id = _token_service.verify_access_token(token)
    except InvalidTokenError:
        log.warning("[get_optional_current_user] Token verification failed: invalid or expired access token")
        return None

    user_repo = AppUserRepository(db)
    user = await user_repo.find_by_id(user_id)
    if user is None or user.status != AppUserStatus.ACTIVE:
        log.warning("[get_optional_current_user] Caller resolution failed: user_id=%s not found or inactive", user_id)
        return None

    org_member_repo = OrganizationMemberRepository(db)
    memberships = await org_member_repo.find_all_active_by_user(user.id)
    org_id = memberships[0].org_id if memberships else None
    roles = await org_member_repo.find_roles_by_user(user.id)

    log.info("[get_optional_current_user] Resolved authenticated caller: user_id=%s, org_id=%s", user.id, org_id)

    return CurrentUser(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        org_id=org_id,
        roles=tuple(roles),
    )


async def get_graphql_context(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser | None = Depends(get_optional_current_user),
) -> GraphQLContext:
    """FastAPI dependency that constructs the GraphQLContext for StrawberryRouter."""
    return GraphQLContext(
        db=db,
        current_user=current_user,
        loaders=RequestLoaders.create(db),
    )
