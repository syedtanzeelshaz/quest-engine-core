from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.datasource_schema_object import DatasourceSchemaObject
from app.repository.base import BaseRepository


class DatasourceSchemaObjectRepository(BaseRepository[DatasourceSchemaObject]):
    """Data access repository for tenant.datasource_schema_object."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DatasourceSchemaObject, session)

    async def find_all_by_datasource(self, datasource_id: int) -> list[DatasourceSchemaObject]:
        """Fetch all discovered schema objects for a datasource."""
        stmt = select(DatasourceSchemaObject).where(
            DatasourceSchemaObject.datasource_id == datasource_id
        )
        res = await self.session.scalars(stmt)
        return list(res.all())

    async def find_all_by_datasource_and_object_name(
        self,
        datasource_id: int,
        object_name: str,
    ) -> list[DatasourceSchemaObject]:
        """Fetch all schema objects matching an object name for a datasource."""
        stmt = select(DatasourceSchemaObject).where(
            DatasourceSchemaObject.datasource_id == datasource_id,
            DatasourceSchemaObject.object_name == object_name,
        )
        res = await self.session.scalars(stmt)
        return list(res.all())
