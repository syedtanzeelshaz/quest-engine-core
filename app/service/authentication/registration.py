"""
RegistrationService — user registration orchestration.

Coordinates email uniqueness check, password hashing, user creation,
and initial JWT token pair issuance (with refresh token persistence).
"""
from app.core.exceptions import EmailAlreadyExistsError
from app.core.transaction import transactional
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair, RegisterCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.token import TokenService


class RegistrationService:
    """Orchestrates new user account creation."""

    def __init__(
        self,
        user_repo: AppUserRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._user_repo = user_repo
        self._refresh_token_repo = refresh_token_repo
        self._password_service = password_service
        self._token_service = token_service

    @transactional
    def register(self, command: RegisterCommand) -> tuple[AppUser, AuthTokenPair]:
        """
        Register a new user account.

        Steps:
            1. Check email uniqueness.
            2. Hash the plain-text password.
            3. Persist the new AppUser (status=ACTIVE).
            4. Issue JWT access + refresh token pair.
            5. Persist the refresh token hash for server-side revocation support.

        Returns:
            Tuple of (created AppUser, AuthTokenPair).

        Raises:
            EmailAlreadyExistsError: if the email is already registered.
        """
        if self._user_repo.exists_by_email(command.email):
            raise EmailAlreadyExistsError(
                f"A user with email '{command.email}' already exists."
            )

        password_hash = self._password_service.hash(command.plain_password)

        user = AppUser(
            email=command.email,
            password_hash=password_hash,
            first_name=command.first_name,
            last_name=command.last_name,
            status=AppUserStatus.ACTIVE,
        )
        user = self._user_repo.save_and_flush(user)

        token_pair = self._token_service.issue_pair(user.id)
        self._persist_refresh_token(user.id, token_pair.refresh_token)

        return user, token_pair

    def _persist_refresh_token(self, user_id: int, raw_refresh_token: str) -> None:
        token_hash = self._token_service.hash_token(raw_refresh_token)
        expires_at = self._token_service.refresh_token_expires_at()
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        self._refresh_token_repo.save_and_flush(refresh_token)
