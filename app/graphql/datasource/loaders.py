"""Datasource domain DataLoaders for batching and N+1 prevention."""
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from app.graphql.common.loaders import batch_fetch_by_id, create_dataloader
from app.graphql.datasource.mappers import datasource_to_type
from app.graphql.datasource.types import DatasourceType
from app.repository.tenant.datasource_repo import DatasourceRepository
from app.service.datasource.datasource_query_service import (
    DatasourceQueryService,
)


async def load_datasources_by_ids(
    keys: Sequence[int],
    db: AsyncSession,
) -> list[DatasourceType | None]:
    """Batch load datasources by their primary key IDs in a single query."""
    datasource_repo = DatasourceRepository(db)
    datasource_query_service = DatasourceQueryService(datasource_repo=datasource_repo)
    return await batch_fetch_by_id(
        name="DatasourceById",
        keys=keys,
        fetch_fn=datasource_query_service.get_by_ids,
        map_fn=datasource_to_type,
    )


async def load_datasources_by_org_ids(
    org_ids: Sequence[int],
    db: AsyncSession,
) -> list[list[DatasourceType]]:
    """Batch load datasources for multiple organizations in a single query."""
    if not org_ids:
        return []

    datasource_repo = DatasourceRepository(db)
    datasource_query_service = DatasourceQueryService(datasource_repo=datasource_repo)
    ds_map = await datasource_query_service.get_by_org_ids(org_ids)

    return [
        [datasource_to_type(ds) for ds in ds_map.get(org_id, [])]
        for org_id in org_ids
    ]


def create_datasource_loader(db: AsyncSession) -> DataLoader[int, DatasourceType | None]:
    """Factory to create a request-scoped DataLoader for Datasource entities."""
    return create_dataloader(
        load_fn=lambda keys: load_datasources_by_ids(keys, db),
    )


def create_org_datasources_loader(db: AsyncSession) -> DataLoader[int, list[DatasourceType]]:
    """Factory to create a request-scoped DataLoader for organization datasources."""
    return create_dataloader(
        load_fn=lambda keys: load_datasources_by_org_ids(keys, db),
    )
