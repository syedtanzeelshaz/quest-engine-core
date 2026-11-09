from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import InvalidCredentialsError, UserNotActiveError
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.member import Member, MemberStatus
from app.model.identity.operator import Operator, OperatorStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.login_service import LoginService
from app.service.authentication.models import AuthTokenPair, LoginCommand
from app.service.authentication.password import PasswordService
from app.service.authentication.token import TokenService


class TestLoginService:
    @pytest.fixture(autouse=True)
    def setup_service(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session

        self.mock_user_repo = MagicMock(spec=AppUserRepository)
        self.mock_user_repo.session = self.mock_session

        self.mock_member_repo = MagicMock(spec=MemberRepository)
        self.mock_member_repo.session = self.mock_session

        self.mock_operator_repo = MagicMock(spec=OperatorRepository)
        self.mock_operator_repo.session = self.mock_session

        self.mock_refresh_token_repo = MagicMock(spec=RefreshTokenRepository)
        self.mock_refresh_token_repo.session = self.mock_session

        self.mock_password_service = MagicMock(spec=PasswordService)
        self.mock_token_service = MagicMock(spec=TokenService)

        self.service = LoginService(
            user_repo=self.mock_user_repo,
            member_repo=self.mock_member_repo,
            operator_repo=self.mock_operator_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            password_service=self.mock_password_service,
            token_service=self.mock_token_service,
        )

        self.dummy_user = AppUser(
            id=1,
            email="test@example.com",
            password_hash="$2b$12$hashedpwd",
            experience=Experience.CUSTOMER,
            status=AppUserStatus.ACTIVE,
        )

        self.dummy_member = Member(
            id=1,
            user_id=1,
            email="test@example.com",
            first_name="Alice",
            last_name="Smith",
            status=MemberStatus.INDIVIDUAL,
        )

        self.dummy_tokens = AuthTokenPair(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_in=900,
        )


    @pytest.mark.anyio
    async def test_authenticate_success(self) -> None:
        self.mock_user_repo.find_by_email_and_experience.return_value = self.dummy_user
        self.mock_password_service.verify.return_value = True
        self.mock_member_repo.find_by_user_id.return_value = self.dummy_member
        self.mock_member_repo.find_roles_by_user_id.return_value = ["MEMBER"]
        self.mock_token_service.issue_pair.return_value = self.dummy_tokens
        self.mock_token_service.hash_token.return_value = "hashed_refresh_token"
        self.mock_token_service.refresh_token_expires_at.return_value = datetime(2026, 10, 1, tzinfo=UTC)

        command = LoginCommand(email="test@example.com", plain_password="validpassword")
        user, tokens = await self.service.authenticate(command)

        assert user == self.dummy_user
        assert tokens == self.dummy_tokens

        # Check repository interactions
        self.mock_user_repo.find_by_email_and_experience.assert_called_once_with(
            email="test@example.com",
            experience=Experience.CUSTOMER,
        )
        self.mock_password_service.verify.assert_called_once_with("validpassword", self.dummy_user.password_hash)
        self.mock_member_repo.find_by_user_id.assert_called_once_with(1)
        self.mock_member_repo.find_roles_by_user_id.assert_called_once_with(1)

        # Check refresh token persistence
        self.mock_refresh_token_repo.save_and_flush.assert_called_once()
        saved_rt: RefreshToken = self.mock_refresh_token_repo.save_and_flush.call_args[0][0]
        assert saved_rt.user_id == 1
        assert saved_rt.token_hash == "hashed_refresh_token"
        assert saved_rt.is_revoked is False


    @pytest.mark.anyio
    async def test_authenticate_user_not_found_raises_invalid_credentials(self) -> None:
        self.mock_user_repo.find_by_email_and_experience.return_value = None

        command = LoginCommand(email="notfound@example.com", plain_password="password")
        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            await self.service.authenticate(command)

        self.mock_password_service.verify.assert_not_called()
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()


    @pytest.mark.anyio
    async def test_authenticate_wrong_password_raises_invalid_credentials(self) -> None:
        self.mock_user_repo.find_by_email_and_experience.return_value = self.dummy_user
        self.mock_password_service.verify.return_value = False

        command = LoginCommand(email="test@example.com", plain_password="wrongpassword")
        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            await self.service.authenticate(command)

        self.mock_refresh_token_repo.save_and_flush.assert_not_called()


    @pytest.mark.anyio
    async def test_authenticate_inactive_user_raises_user_not_active_error(self) -> None:
        inactive_user = AppUser(
            id=2,
            email="inactive@example.com",
            password_hash="$2b$12$hashedpwd",
            experience=Experience.CUSTOMER,
            status=AppUserStatus.INACTIVE,
        )
        self.mock_user_repo.find_by_email_and_experience.return_value = inactive_user
        self.mock_password_service.verify.return_value = True

        command = LoginCommand(email="inactive@example.com", plain_password="validpassword")
        with pytest.raises(UserNotActiveError, match="not active"):
            await self.service.authenticate(command)

        self.mock_refresh_token_repo.save_and_flush.assert_not_called()


    @pytest.mark.anyio
    async def test_authenticate_experience_mismatch_raises_invalid_credentials(self) -> None:
        # Repository queries with experience=OPERATIONS and finds no matching record
        self.mock_user_repo.find_by_email_and_experience.return_value = None

        command = LoginCommand(
            email="test@example.com",
            plain_password="validpassword",
            experience=Experience.OPERATIONS,
        )
        with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
            await self.service.authenticate(command)

        self.mock_user_repo.find_by_email_and_experience.assert_called_once_with(
            email="test@example.com",
            experience=Experience.OPERATIONS,
        )
        self.mock_password_service.verify.assert_not_called()
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()
