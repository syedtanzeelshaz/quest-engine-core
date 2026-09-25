"""User domain DataLoaders for batching and N+1 prevention."""
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.graphql.common.loaders import batch_fetch_by_id, create_dataloader
from app.graphql.user.mappers import user_to_type
from app.graphql.user.types import UserType
from app.repository.identity.app_user_repo import AppUserRepository
from app.service.user.user_query_service import UserQueryService


async def load_users_by_ids(keys: Sequence[int], db: AsyncSession) -> list[UserType | None]:
    """Batch load users by their primary key IDs in a single query."""
    user_repo = AppUserRepository(db)
    user_query_service = UserQueryService(user_repo=user_repo)
    return await batch_fetch_by_id(
        name="UserById",
        keys=keys,
        fetch_fn=user_query_service.get_by_ids,
        map_fn=user_to_type,
    )


def create_user_loader(db: AsyncSession) -> DataLoader[int, UserType | None]:
    """Factory to create a request-scoped DataLoader for User entities with max batch limit."""
    return create_dataloader(
        load_fn=lambda keys: load_users_by_ids(keys, db),
    )
