"""
Authentication service factory.

Pure Python factory functions to construct authentication domain services.
Completely framework-agnostic (zero FastAPI imports). Safe to use across REST,
GraphQL, WebSocket, background tasks, CLI scripts, and unit tests.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.login_service import LoginService
from app.service.authentication.password import PasswordService
from app.service.authentication.registration_service import RegistrationService
from app.service.authentication.token import TokenService
from app.service.authentication.token_refresh_service import TokenRefreshService

# ──────────────────────────────────────────────
# Singletons (stateless, no DB session needed)
# ──────────────────────────────────────────────
_password_service = PasswordService()
_token_service = TokenService(settings)


def get_password_service() -> PasswordService:
    """Return the shared PasswordService singleton."""
    return _password_service


def get_token_service() -> TokenService:
    """Return the shared TokenService singleton."""
    return _token_service


# ──────────────────────────────────────────────
# Service builders
# ──────────────────────────────────────────────
def build_login_service(session: AsyncSession | None = None) -> LoginService:
    """Construct a LoginService wired with all repository and service dependencies."""
    return LoginService(
        user_repo=AppUserRepository(session),
        member_repo=MemberRepository(session),
        operator_repo=OperatorRepository(session),
        refresh_token_repo=RefreshTokenRepository(session),
        password_service=_password_service,
        token_service=_token_service,
    )


def build_registration_service(session: AsyncSession | None = None) -> RegistrationService:
    """Construct a RegistrationService wired with all repository and service dependencies."""
    return RegistrationService(
        user_repo=AppUserRepository(session),
        member_repo=MemberRepository(session),
        operator_repo=OperatorRepository(session),
        refresh_token_repo=RefreshTokenRepository(session),
        password_service=_password_service,
        token_service=_token_service,
    )


def build_token_refresh_service(session: AsyncSession | None = None) -> TokenRefreshService:
    """Construct a TokenRefreshService wired with all repository and service dependencies."""
    return TokenRefreshService(
        user_repo=AppUserRepository(session),
        member_repo=MemberRepository(session),
        operator_repo=OperatorRepository(session),
        refresh_token_repo=RefreshTokenRepository(session),
        token_service=_token_service,
    )
