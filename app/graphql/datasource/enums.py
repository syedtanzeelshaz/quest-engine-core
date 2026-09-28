"""Datasource domain GraphQL enums."""
import strawberry

from app.model.tenant.datasource import (
    DatasourceApprovalStatus,
    DatasourceCategory,
    DatasourceKind,
    DatasourceStatus,
)

DatasourceCategory = strawberry.enum(
    DatasourceCategory,
    name="DatasourceCategory",
    description="Broad high-level category of the data source.",
)

DatasourceKind = strawberry.enum(
    DatasourceKind,
    name="DatasourceKind",
    description="Specific database engine or document platform kind.",
)

DatasourceApprovalStatus = strawberry.enum(
    DatasourceApprovalStatus,
    name="DatasourceApprovalStatus",
    description="Administrative approval state of the datasource.",
)

DatasourceStatus = strawberry.enum(
    DatasourceStatus,
    name="DatasourceStatus",
    description="Operational connection and lifecycle status of the datasource.",
)

__all__ = [
    "DatasourceApprovalStatus",
    "DatasourceCategory",
    "DatasourceKind",
    "DatasourceStatus",
]
