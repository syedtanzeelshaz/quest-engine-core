from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.tenant.datasource_schema_object import DatasourceSchemaObject
from app.repository.base import BaseRepository


class DatasourceSchemaObjectRepository(BaseRepository[DatasourceSchemaObject]):
    """Data access repository for tenant.datasource_schema_object."""

    def __init__(self, session: Session) -> None:
        super().__init__(DatasourceSchemaObject, session)

    def find_all_by_datasource(
        self,
        datasource_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DatasourceSchemaObject]:
        """Fetch all discovered schema objects for a datasource."""
        stmt = (
            select(DatasourceSchemaObject)
            .where(DatasourceSchemaObject.datasource_id == datasource_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def find_all_by_datasource_and_object_name(
        self,
        datasource_id: int,
        object_name: str,
    ) -> list[DatasourceSchemaObject]:
        """Fetch all schema objects matching an object name for a datasource."""
        stmt = select(DatasourceSchemaObject).where(
            DatasourceSchemaObject.datasource_id == datasource_id,
            DatasourceSchemaObject.object_name == object_name,
        )
        return list(self.session.scalars(stmt).all())
