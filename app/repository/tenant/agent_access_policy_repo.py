from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.tenant.agent_access_policy import AgentAccessPolicy
from app.repository.base import BaseRepository


class AgentAccessPolicyRepository(BaseRepository[AgentAccessPolicy]):
    """Data access repository for tenant.agent_access_policy."""

    def __init__(self, session: Session) -> None:
        super().__init__(AgentAccessPolicy, session)

    def find_all_by_agent(
        self,
        agent_id: int,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AgentAccessPolicy]:
        """Fetch all access policies defined for an agent."""
        stmt = (
            select(AgentAccessPolicy)
            .where(
                AgentAccessPolicy.agent_id == agent_id,
                AgentAccessPolicy.org_id == org_id,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())
