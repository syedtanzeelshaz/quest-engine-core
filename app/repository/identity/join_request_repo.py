from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity.join_request import JoinRequest
from app.repository.base import BaseRepository


class JoinRequestRepository(BaseRepository[JoinRequest]):
    """Data access repository for identity.join_request."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(JoinRequest, session)

