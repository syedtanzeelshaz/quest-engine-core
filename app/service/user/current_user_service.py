"""
CurrentUserService — resolves and validates the authenticated user from access tokens.

Coordinates token cryptographic verification with user account existence, status checks,
and persona scope resolution (Customer / Operations).
"""
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import (
    UserNotActiveError,
    UserNotFoundError,
)
from app.model.identity.app_user import AppUser, AppUserStatus
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.service.authentication.token import TokenService
from app.service.user.models import CurrentUser, UserScopes


class CurrentUserService:
    """Resolves and validates the active authenticated user into a sanitized CurrentUser context."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        token_service: TokenService,
        member_repo: MemberRepository | None = None,
        operator_repo: OperatorRepository | None = None,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service
        self._member_repo = member_repo if member_repo is not None else MemberRepository()
        self._operator_repo = operator_repo if operator_repo is not None else OperatorRepository()


    async def get_user_from_token(self, raw_token: str) -> CurrentUser:
        """
        Verify an access token and return the sanitized active CurrentUser context.

        Raises:
            InvalidTokenError: If token is expired, malformed, or not an access token.
            UserNotFoundError: If the user ID in the token does not exist.
            UserNotActiveError: If the user account exists but is not ACTIVE.
        """
        user_id = self._token_service.verify_access_token(raw_token)
        return await self.get_active_user_by_id(user_id)


    async def get_active_user_by_id(self, user_id: int) -> CurrentUser:
        """
        Fetch an active user by their primary key ID and resolve their persona context.

        Raises:
            UserNotFoundError: If the user ID does not exist.
            UserNotActiveError: If the user account exists but is not ACTIVE.
        """
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} does not exist.")

        if user.status != AppUserStatus.ACTIVE:
            raise UserNotActiveError(
                f"User account is not active (status={user.status})."
            )

        return await self._build_current_user(user)


    async def _build_current_user(self, user: AppUser) -> CurrentUser:
        """Assemble the sanitized CurrentUser dataclass with persona details and scopes."""
        first_name: str | None = None
        last_name: str | None = None
        roles: list[str] = []
        scopes = UserScopes()

        experience = (
            user.experience
            if isinstance(user.experience, Experience)
            else Experience(user.experience)
            if user.experience
            else Experience.CUSTOMER
        )
        status = (
            user.status
            if isinstance(user.status, AppUserStatus)
            else AppUserStatus(user.status)
            if user.status
            else AppUserStatus.ACTIVE
        )

        if experience == Experience.OPERATIONS:
            operator = await self._operator_repo.find_by_user_id(user.id)
            if operator:
                first_name = operator.first_name
                last_name = operator.last_name
                scopes = UserScopes(operator_id=operator.id)
            roles = await self._operator_repo.find_roles_by_user_id(user.id)
        else:
            member = await self._member_repo.find_by_user_id(user.id)
            if member:
                first_name = member.first_name
                last_name = member.last_name
                scopes = UserScopes(member_id=member.id, org_id=member.org_id)
            roles = await self._member_repo.find_roles_by_user_id(user.id)

        return CurrentUser(
            id=user.id,
            email=user.email,
            experience=experience,
            status=status,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            scopes=scopes,
        )

