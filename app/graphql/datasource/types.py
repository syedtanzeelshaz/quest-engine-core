"""Datasource domain GraphQL output types."""
from datetime import datetime

import strawberry

from app.graphql.datasource.enums import (
    DatasourceApprovalStatus,
    DatasourceCategory,
    DatasourceKind,
    DatasourceStatus,
)


@strawberry.type(name="Datasource", description="Datasource entity representation.")
class DatasourceType:
    id: strawberry.ID
    org_id: strawberry.ID
    name: str
    category: DatasourceCategory
    kind: DatasourceKind
    approval_status: DatasourceApprovalStatus | None = None
    status: DatasourceStatus | None = None
    reviewed_by: strawberry.ID | None = None
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
