from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.identity.join_request import JoinRequest, JoinRequestStatus
from app.repository.base import BaseRepository


class JoinRequestRepository(BaseRepository[JoinRequest]):
    """Data access repository for identity.join_request."""

    def __init__(self, session: Session) -> None:
        super().__init__(JoinRequest, session)

    def find_pending_by_user_and_org(
        self, user_id: int, org_id: int
    ) -> JoinRequest | None:
        """Fetch an existing PENDING join request or invitation between a user and organization."""
        stmt = (
            select(JoinRequest)
            .where(
                JoinRequest.user_id == user_id,
                JoinRequest.org_id == org_id,
                JoinRequest.status == JoinRequestStatus.PENDING,
            )
            .limit(1)
        )
        return self.session.scalar(stmt)

    def find_all_by_org(self, org_id: int) -> list[JoinRequest]:
        """Fetch all requests or invitations for an organization."""
        stmt = select(JoinRequest).where(JoinRequest.org_id == org_id)
        return list(self.session.scalars(stmt).all())

    def find_all_by_user(self, user_id: int) -> list[JoinRequest]:
        """Fetch all requests or invitations involving a specific user."""
        stmt = select(JoinRequest).where(JoinRequest.user_id == user_id)
        return list(self.session.scalars(stmt).all())
