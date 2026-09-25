"""User domain GraphQL query fetchers."""
import strawberry
from strawberry.types import Info

from app.graphql.common.constants import GraphQLMessage
from app.graphql.common.context import GraphQLContext
from app.graphql.common.permissions import IsAuthenticated
from app.graphql.user import mappers
from app.graphql.user.types import UserType
from app.repository.identity.app_user_repo import AppUserRepository
from app.service.user.user_service import UserService
from app.util.logger import log


@strawberry.type
class UserDataFetcher:
    """User domain query operations."""

    @strawberry.field(
        description="Retrieve profile details for the currently authenticated user.",
        permission_classes=[IsAuthenticated],
    )
    async def current_user(self, info: Info[GraphQLContext, None]) -> UserType:
        current_user = info.context.require_user()
        log.info("[current_user] Fetching profile for user_id=%s", current_user.id)

        user_repo = AppUserRepository(info.context.db)
        user_service = UserService(user_repo=user_repo)

        user = await user_service.get_user_by_id(current_user.id)
        if user is None:
            log.warning("[current_user] User not found for user_id=%s", current_user.id)
            raise Exception(GraphQLMessage.USER_NOT_FOUND)

        return mappers.user_to_type(user)
