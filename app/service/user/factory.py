"""
User service factory.

Pure Python factory functions to construct user domain services.
Completely framework-agnostic (zero FastAPI imports). Safe to use across REST,
GraphQL, WebSocket, background tasks, CLI scripts, and unit tests.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.service.authentication.factory import get_token_service
from app.service.user.current_user_service import CurrentUserService


def build_current_user_service(session: AsyncSession | None = None) -> CurrentUserService:
    """Construct a CurrentUserService wired with repository and token dependencies."""
    return CurrentUserService(
        user_repo=AppUserRepository(session),
        token_service=get_token_service(),
        member_repo=MemberRepository(session),
        operator_repo=OperatorRepository(session),
    )

