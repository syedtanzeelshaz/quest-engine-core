"""
GraphQL Context & Request Loader definitions.

Provides per-request state propagation (Database session, CurrentUser, and DataLoaders)
to all GraphQL field resolvers via Strawberry's Info object.
"""
from dataclasses import dataclass, field

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.api.constants import AUTH_TOKEN_URL
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import InvalidTokenError
from app.model.identity.app_user import AppUserStatus
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.organization_member_repo import (
    OrganizationMemberRepository,
)
from app.service.authentication.models import CurrentUser
from app.service.authentication.token import TokenService

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=AUTH_TOKEN_URL,
    auto_error=False,
)
_token_service = TokenService(settings)


@dataclass
class RequestLoaders:
    """
    Per-request DataLoaders container.

    Instantiated once per GraphQL request in get_graphql_context to batch queries
    across nested resolvers and prevent cross-request cache leaks.
    Domain-specific loaders will be attached here as domains are introduced.
    """
    pass


@dataclass
class GraphQLContext(BaseContext):
    """Context object available to every Strawberry resolver via info.context."""
    db: AsyncSession
    current_user: CurrentUser | None = None
    loaders: RequestLoaders = field(default_factory=RequestLoaders)


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
        return None

    user = await AppUserRepository(db).find_by_id(user_id)
    if user is None or user.status != AppUserStatus.ACTIVE:
        return None

    org_member_repo = OrganizationMemberRepository(db)
    memberships = await org_member_repo.find_all_active_by_user(user.id)
    org_id = memberships[0].org_id if memberships else None
    roles = await org_member_repo.find_roles_by_user(user.id)

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
        loaders=RequestLoaders(),
    )
