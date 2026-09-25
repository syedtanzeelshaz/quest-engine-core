"""User domain GraphQL mutation resolvers."""
import strawberry
from strawberry.types import Info

from app.graphql.common.context import GraphQLContext
from app.graphql.common.permissions import IsAuthenticated
from app.graphql.user import mappers
from app.graphql.user.inputs import UpdateUserProfileInput
from app.graphql.user.types import UserType
from app.repository.identity.app_user_repo import AppUserRepository
from app.service.user.user_service import UserService
from app.util.logger import log


@strawberry.type
class UserDataMutator:
    """User domain mutation operations."""

    @strawberry.mutation(
        description="Update profile details for the currently authenticated user.",
        permission_classes=[IsAuthenticated],
    )
    async def update_user_profile(
        self,
        info: Info[GraphQLContext, None],
        input: UpdateUserProfileInput,
    ) -> UserType:
        ctx = info.context
        current_user = ctx.require_user()
        log.info("[update_user_profile] Mutation request received for user_id=%s", current_user.id)

        user_repo = AppUserRepository(ctx.db)
        user_service = UserService(user_repo=user_repo)

        updated_user = await user_service.update_profile(
            user_id=current_user.id,
            input_data=input,
        )

        return mappers.user_to_type(updated_user)
