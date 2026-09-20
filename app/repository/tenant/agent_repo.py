from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.tenant.agent import Agent, AgentStatus
from app.repository.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Data access repository for tenant.agent."""

    def __init__(self, session: Session) -> None:
        super().__init__(Agent, session)

    def find_all_by_org(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Agent]:
        """Fetch all agents belonging to an organization with pagination."""
        stmt = select(Agent).where(Agent.org_id == org_id).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def count_by_org(self, org_id: int) -> int:
        """Count total agents belonging to an organization."""
        stmt = select(func.count()).select_from(Agent).where(Agent.org_id == org_id)
        return self.session.scalar(stmt) or 0

    def find_all_by_name_and_org(self, name: str, org_id: int) -> list[Agent]:
        """Fetch all agents matching a name within an organization."""
        stmt = select(Agent).where(
            Agent.name == name,
            Agent.org_id == org_id,
        )
        return list(self.session.scalars(stmt).all())

    def exists_by_name_and_org(self, name: str, org_id: int) -> bool:
        """Check whether an agent with the given name exists in an organization."""
        stmt = (
            select(1)
            .select_from(Agent)
            .where(Agent.name == name, Agent.org_id == org_id)
            .limit(1)
        )
        return self.session.scalar(stmt) is not None

    def find_all_active_by_org(
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
