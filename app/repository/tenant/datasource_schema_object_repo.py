from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.tenant.datasource_schema_object import DatasourceSchemaObject, SchemaObjectType
from app.repository.base import BaseRepository


class DatasourceSchemaObjectRepository(BaseRepository[DatasourceSchemaObject]):
    """Data access repository for tenant.datasource_schema_object."""

    def __init__(self, session: Session) -> None:
        super().__init__(DatasourceSchemaObject, session)

    def find_all_by_datasource(
        self,
        datasource_id: int,
        org_id: int,
        object_type: SchemaObjectType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[DatasourceSchemaObject]:
        """Fetch discovered schema objects for a datasource, optionally filtered by type."""
        stmt = select(DatasourceSchemaObject).where(
            DatasourceSchemaObject.datasource_id == datasource_id,
            DatasourceSchemaObject.org_id == org_id,
        )
        if object_type is not None:
            stmt = stmt.where(DatasourceSchemaObject.object_type == object_type)
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def find_by_object_name(
        self,
        datasource_id: int,
        object_name: str,
        org_id: int,
    ) -> DatasourceSchemaObject | None:
        """Fetch a specific schema object by name for a datasource."""
        stmt = select(DatasourceSchemaObject).where(
            DatasourceSchemaObject.datasource_id == datasource_id,
            DatasourceSchemaObject.object_name == object_name,
            DatasourceSchemaObject.org_id == org_id,
        )
        return self.session.scalar(stmt)
