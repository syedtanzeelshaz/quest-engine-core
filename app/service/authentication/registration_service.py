"""
RegistrationService — user registration orchestration.

Coordinates email uniqueness check, password hashing, user creation,
member persona provisioning (INDIVIDUAL status), and initial JWT token pair issuance.
"""
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import EmailAlreadyExistsError
from app.core.transaction import transactional
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.member import Member, MemberStatus
from app.model.identity.operator import Operator, OperatorStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair, RegisterCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.token import TokenService


class RegistrationService:
    """Orchestrates new user account and member/operator persona creation."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        member_repo: MemberRepository,
        operator_repo: OperatorRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._member_repo = member_repo
        self._operator_repo = operator_repo
        self._refresh_token_repo = refresh_token_repo
        self._password_service = password_service
        self._token_service = token_service


    @transactional
    async def register(self, command: RegisterCommand) -> tuple[AppUser, Member | Operator, AuthTokenPair]:
        """
        Register a new user account and provision their initial persona based on experience.

        Steps:
            1. Check email uniqueness.
            2. Hash the plain-text password.
            3. Persist the new AppUser (experience=command.experience, status=ACTIVE).
            4. Persist the corresponding persona:
               - OPERATIONS -> Operator (status=ACTIVE, corporate_email=command.email)
               - CUSTOMER -> Member (status=INDIVIDUAL, org_id=None)
            5. Issue JWT access + refresh token pair with experience & names.
            6. Persist the refresh token hash for server-side revocation support.

        Returns:
            Tuple of (created AppUser, created persona (Member or Operator), AuthTokenPair).

        Raises:
            EmailAlreadyExistsError: if the email is already registered.
        """
        if await self._user_repo.exists_by_email(command.email):
            raise EmailAlreadyExistsError(
                f"A user with email '{command.email}' already exists."
            )

        password_hash = await self._password_service.hash(command.plain_password)

        user = AppUser(
            email=command.email,
            password_hash=password_hash,
            experience=command.experience,
            status=AppUserStatus.ACTIVE,
        )
        user = await self._user_repo.save_and_flush(user)

        persona: Member | Operator
        if command.experience == Experience.OPERATIONS:
            persona = Operator(
                user_id=user.id,
                first_name=command.first_name,
                last_name=command.last_name,
                corporate_email=command.email,
                status=OperatorStatus.ACTIVE,
            )
            persona = await self._operator_repo.save_and_flush(persona)
        else:
            persona = Member(
                user_id=user.id,
                email=command.email,
                first_name=command.first_name,
                last_name=command.last_name,
                org_id=None,
                status=MemberStatus.INDIVIDUAL,
            )
            persona = await self._member_repo.save_and_flush(persona)

        token_pair = self._token_service.issue_pair(
            user_id=user.id,
            email=user.email,
            experience=user.experience,
            first_name=persona.first_name,
            last_name=persona.last_name,
            roles=None,  # No organization roles on initial registration
        )
        await self._persist_refresh_token(user.id, token_pair.refresh_token)

        return user, persona, token_pair


    async def _persist_refresh_token(self, user_id: int, raw_refresh_token: str) -> None:
        token_hash = self._token_service.hash_token(raw_refresh_token)
        expires_at = self._token_service.refresh_token_expires_at()
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        await self._refresh_token_repo.save_and_flush(refresh_token)
