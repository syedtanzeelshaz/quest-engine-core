from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.tenant.datasource import (
    Datasource,
    DatasourceApprovalStatus,
    DatasourceStatus,
)
from app.repository.base import BaseRepository


class DatasourceRepository(BaseRepository[Datasource]):
    """Data access repository for tenant.datasource."""

    def __init__(self, session: Session) -> None:
        super().__init__(Datasource, session)

    def find_all_by_org(self, org_id: int) -> list[Datasource]:
        """Fetch all datasources belonging to an organization."""
        stmt = select(Datasource).where(Datasource.org_id == org_id)
        return list(self.session.scalars(stmt).all())

    def count_by_org(self, org_id: int) -> int:
        """Count total datasources belonging to an organization."""
        stmt = (
            select(func.count())
            .select_from(Datasource)
            .where(Datasource.org_id == org_id)
        )
        return self.session.scalar(stmt) or 0

    def find_all_by_name_and_org(self, name: str, org_id: int) -> list[Datasource]:
        """Fetch all datasources matching a name within an organization."""
        stmt = select(Datasource).where(
            Datasource.name == name,
            Datasource.org_id == org_id,
        )
        return list(self.session.scalars(stmt).all())

    def exists_by_name_and_org(self, name: str, org_id: int) -> bool:
        """Check whether a datasource with the given name exists in an organization."""
        stmt = (
            select(1)
            .select_from(Datasource)
            .where(Datasource.name == name, Datasource.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_all_active_by_org(self, org_id: int) -> list[Datasource]:
        """Fetch all operational and approved datasources for an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.status == DatasourceStatus.ACTIVE,
                Datasource.approval_status == DatasourceApprovalStatus.APPROVED,
            )
        )
        return list(self.session.scalars(stmt).all())

    def find_all_by_org_and_approval_status(
        self,
        org_id: int,
        approval_status: DatasourceApprovalStatus,
    ) -> list[Datasource]:
        """Fetch datasources by approval status within an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.approval_status == approval_status,
            )
        )
        return list(self.session.scalars(stmt).all())

    def find_all_by_org_and_status(
        self,
        org_id: int,
        status: DatasourceStatus,
    ) -> list[Datasource]:
        """Fetch datasources by operational status within an organization."""
        stmt = (
            select(Datasource)
            .where(
                Datasource.org_id == org_id,
                Datasource.status == status,
            )
        )
        return list(self.session.scalars(stmt).all())
