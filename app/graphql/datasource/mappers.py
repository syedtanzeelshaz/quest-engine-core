"""Datasource domain translation mappers: ORM entity -> GraphQL type."""
import strawberry

from app.graphql.datasource.types import DatasourceType
from app.model.tenant.datasource import Datasource


def datasource_to_type(datasource: Datasource) -> DatasourceType:
    """
    Pure translation function mapping a Datasource ORM model to a DatasourceType GraphQL instance.
    Does not perform any I/O or database queries.
    """
    return DatasourceType(
        id=strawberry.ID(str(datasource.id)),
        org_id=strawberry.ID(str(datasource.org_id)),
        name=datasource.name,
        category=datasource.category,
        kind=datasource.kind,
        approval_status=datasource.approval_status,
        status=datasource.status,
        reviewed_by=strawberry.ID(str(datasource.reviewed_by)) if datasource.reviewed_by is not None else None,
        reviewed_at=datasource.reviewed_at,
        created_at=datasource.created_at,
        updated_at=datasource.updated_at,
    )
