"""Organization domain DataLoaders for batching and N+1 prevention."""
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.graphql.common.loaders import batch_fetch_by_id, create_dataloader
from app.graphql.organization.mappers import organization_to_type
from app.graphql.organization.types import OrganizationType
from app.graphql.user.mappers import user_to_type
from app.graphql.user.types import UserType
from app.repository.identity.organization_repo import OrganizationRepository
from app.service.organization.organization_query_service import (
    OrganizationQueryService,
)


async def load_organizations_by_ids(
    keys: Sequence[int],
    db: AsyncSession,
) -> list[OrganizationType | None]:
    """Batch load organizations by their primary key IDs in a single query."""
    org_repo = OrganizationRepository(db)
    org_query_service = OrganizationQueryService(org_repo=org_repo)
    return await batch_fetch_by_id(
        name="OrganizationById",
        keys=keys,
        fetch_fn=org_query_service.get_by_ids,
        map_fn=organization_to_type,
    )


async def load_users_by_org_ids(
    org_ids: Sequence[int],
    db: AsyncSession,
) -> list[list[UserType]]:
    """Batch load active members for multiple organizations in a single query."""
    if not org_ids:
        return []

    org_repo = OrganizationRepository(db)
    org_query_service = OrganizationQueryService(org_repo=org_repo)
    users_with_org = await org_query_service.get_active_users_by_org_ids(org_ids)

    org_users_map: dict[int, list[UserType]] = {org_id: [] for org_id in org_ids}
    for org_id, app_user in users_with_org:
        org_users_map[org_id].append(user_to_type(app_user))

    return [org_users_map[org_id] for org_id in org_ids]


def create_organization_loader(db: AsyncSession) -> DataLoader[int, OrganizationType | None]:
    """Factory to create a request-scoped DataLoader for Organization entities."""
    return create_dataloader(
        load_fn=lambda keys: load_organizations_by_ids(keys, db),
    )


def create_org_users_loader(db: AsyncSession) -> DataLoader[int, list[UserType]]:
    """Factory to create a request-scoped DataLoader for Organization members."""
    return create_dataloader(
        load_fn=lambda keys: load_users_by_org_ids(keys, db),
    )
