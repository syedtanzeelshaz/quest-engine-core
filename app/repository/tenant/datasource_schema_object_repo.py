from sqlalchemy.ext.asyncio import AsyncSession

from app.model.tenant.datasource_schema_object import DatasourceSchemaObject
from app.repository.base import BaseRepository


class DatasourceSchemaObjectRepository(BaseRepository[DatasourceSchemaObject]):
    """Data access repository for tenant.datasource_schema_object."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DatasourceSchemaObject, session)

