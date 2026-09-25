from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.primitives.exceptions import EmailAlreadyExistsError
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair, RegisterCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.registration import RegistrationService
from app.service.authentication.token import TokenService


class TestRegistrationService:
    @pytest.fixture(autouse=True)
    def setup_service(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session

        self.mock_user_repo = MagicMock(spec=AppUserRepository)
        self.mock_user_repo.session = self.mock_session

        self.mock_refresh_token_repo = MagicMock(spec=RefreshTokenRepository)
        self.mock_refresh_token_repo.session = self.mock_session

        self.mock_password_service = MagicMock(spec=PasswordService)
        self.mock_token_service = MagicMock(spec=TokenService)

        self.service = RegistrationService(
            user_repo=self.mock_user_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
        )

        self.dummy_command = RegisterCommand(
            email="newuser@example.com",
            plain_password="StrongPassword123!",
            first_name="Bob",
            last_name="Builder",
        )

        self.dummy_saved_user = AppUser(
            id=10,
            email="newuser@example.com",
            password_hash="$2b$12$hashedpwd",
            first_name="Bob",
            last_name="Builder",
            status=AppUserStatus.ACTIVE,
        )

        self.dummy_tokens = AuthTokenPair(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_in=900,
        )

    @pytest.mark.anyio
    async def test_register_success(self) -> None:
        self.mock_user_repo.exists_by_email.return_value = False
        self.mock_password_service.hash.return_value = "$2b$12$hashedpwd"
        self.mock_user_repo.save_and_flush.return_value = self.dummy_saved_user
        self.mock_token_service.issue_pair.return_value = self.dummy_tokens
        self.mock_token_service.hash_token.return_value = "hashed_refresh_token"
        self.mock_token_service.refresh_token_expires_at.return_value = datetime(2026, 10, 1, tzinfo=UTC)

        user, tokens = await self.service.register(self.dummy_command)

        assert user == self.dummy_saved_user
        assert tokens == self.dummy_tokens

        # Check user uniqueness check and creation
        self.mock_user_repo.exists_by_email.assert_called_once_with("newuser@example.com")
        self.mock_password_service.hash.assert_called_once_with("StrongPassword123!")

        saved_user: AppUser = self.mock_user_repo.save_and_flush.call_args[0][0]
        assert saved_user.email == "newuser@example.com"
        assert saved_user.password_hash == "$2b$12$hashedpwd"
        assert saved_user.status == AppUserStatus.ACTIVE

        # Check refresh token persistence
        self.mock_refresh_token_repo.save_and_flush.assert_called_once()
        saved_rt: RefreshToken = self.mock_refresh_token_repo.save_and_flush.call_args[0][0]
        assert saved_rt.user_id == 10
        assert saved_rt.token_hash == "hashed_refresh_token"
        assert saved_rt.is_revoked is False

    @pytest.mark.anyio
    async def test_register_duplicate_email_raises_error(self) -> None:
        self.mock_user_repo.exists_by_email.return_value = True

        with pytest.raises(EmailAlreadyExistsError, match="already exists"):
            await self.service.register(self.dummy_command)

        self.mock_password_service.hash.assert_not_called()
        self.mock_user_repo.save_and_flush.assert_not_called()
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()

