from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.tenant.agent import Agent, AgentStatus
from app.repository.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Data access repository for tenant.agent enforcing org_id isolation."""

    def __init__(self, session: Session) -> None:
        super().__init__(Agent, session)

    def find_by_id_and_org(self, id: int, org_id: int) -> Agent | None:
        """Fetch a single agent by ID scoped to an organization."""
        stmt = select(Agent).where(
            Agent.id == id,
            Agent.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def find_all_by_org(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agent]:
        """Fetch all agents belonging to an organization with pagination."""
        stmt = (
            select(Agent)
            .where(Agent.org_id == org_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def delete_by_id_and_org(self, id: int, org_id: int) -> bool:
        """Delete an agent by ID scoped to an organization."""
        obj = self.find_by_id_and_org(id, org_id)
        if obj is not None:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def count_by_org(self, org_id: int) -> int:
        """Count total agents belonging to an organization."""
        stmt = select(func.count()).select_from(Agent).where(Agent.org_id == org_id)
        return self.session.scalar(stmt) or 0

    def exists_by_id_and_org(self, id: int, org_id: int) -> bool:
        """Check whether an agent exists for the given ID and organization."""
        stmt = (
            select(1)
            .select_from(Agent)
            .where(Agent.id == id, Agent.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_by_name_and_org(self, name: str, org_id: int) -> Agent | None:
        """Fetch an agent by name within an organization."""
        stmt = select(Agent).where(
            Agent.name == name,
            Agent.org_id == org_id,
        )
        return self.session.scalar(stmt)

    def exists_by_name_and_org(self, name: str, org_id: int) -> bool:
        """Check whether an agent with the given name exists in an organization."""
        stmt = (
            select(1)
            .select_from(Agent)
            .where(Agent.name == name, Agent.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_active_by_org(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agent]:
        """Fetch all active agents for an organization."""
        stmt = (
            select(Agent)
            .where(
                Agent.org_id == org_id,
                Agent.status == AgentStatus.ACTIVE,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
