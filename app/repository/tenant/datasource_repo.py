from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.tenant.datasource import (
    Datasource,
    DatasourceApprovalStatus,
    DatasourceStatus,
)
from app.repository.base import BaseRepository


class DatasourceRepository(BaseRepository[Datasource]):
    """Data access repository for tenant.datasource enforcing org_id isolation."""

    def __init__(self, session: Session) -> None:
        super().__init__(Datasource, session)

    def find_by_id_and_org(self, id: int, org_id: int) -> Datasource | None:
        """Fetch a single datasource by ID scoped to an organization."""
        stmt = select(Datasource).where(
            Datasource.id == id,
            Datasource.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def find_all_by_org(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Datasource]:
        """Fetch all datasources belonging to an organization with pagination."""
        stmt = (
            select(Datasource)
            .where(Datasource.org_id == org_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def delete_by_id_and_org(self, id: int, org_id: int) -> bool:
        """Delete a datasource by ID scoped to an organization."""
        obj = self.find_by_id_and_org(id, org_id)
        if obj is not None:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def count_by_org(self, org_id: int) -> int:
        """Count total datasources belonging to an organization."""
        stmt = select(func.count()).select_from(Datasource).where(Datasource.org_id == org_id)
        return self.session.scalar(stmt) or 0

    def exists_by_id_and_org(self, id: int, org_id: int) -> bool:
        """Check whether a datasource exists for the given ID and organization."""
        stmt = (
            select(1)
            .select_from(Datasource)
            .where(Datasource.id == id, Datasource.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_by_name_and_org(self, name: str, org_id: int) -> Datasource | None:
        """Fetch a datasource by name within an organization."""
        stmt = select(Datasource).where(
            Datasource.name == name,
            Datasource.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def exists_by_name_and_org(self, name: str, org_id: int) -> bool:
        """Check whether a datasource with the given name exists in an organization."""
        stmt = (
            select(1)
            .select_from(Datasource)
            .where(Datasource.name == name, Datasource.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_active_by_org(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Datasource]:
        """Fetch all operational and approved datasources for an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.status == DatasourceStatus.ACTIVE,
                Datasource.approval_status == DatasourceApprovalStatus.APPROVED,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def find_by_approval_status(
        self,
        org_id: int,
        approval_status: DatasourceApprovalStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Datasource]:
        """Fetch datasources by approval status within an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.approval_status == approval_status,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def find_by_status(
        self,
        org_id: int,
        status: DatasourceStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Datasource]:
        """Fetch datasources by operational status within an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.status == status,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
