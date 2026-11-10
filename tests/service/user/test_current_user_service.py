from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import (
    InvalidTokenError,
    UserNotActiveError,
    UserNotFoundError,
)
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.member import Member, MemberStatus
from app.model.identity.operator import Operator, OperatorStatus
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.member_repo import MemberRepository
from app.repository.identity.operator_repo import OperatorRepository
from app.service.authentication.token import TokenService
from app.service.user.current_user_service import CurrentUserService
from app.service.user.factory import build_current_user_service
from app.service.user.models import CurrentUser, UserScopes


class TestCurrentUserService:
    @pytest.fixture(autouse=True)
    def setup_service(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session

        self.mock_user_repo = MagicMock(spec=AppUserRepository)
        self.mock_user_repo.session = self.mock_session

        self.mock_member_repo = MagicMock(spec=MemberRepository)
        self.mock_member_repo.session = self.mock_session

        self.mock_operator_repo = MagicMock(spec=OperatorRepository)
        self.mock_operator_repo.session = self.mock_session

        self.mock_token_service = MagicMock(spec=TokenService)

        self.service = CurrentUserService(
            user_repo=self.mock_user_repo,
            token_service=self.mock_token_service,
            member_repo=self.mock_member_repo,
            operator_repo=self.mock_operator_repo,
        )

        self.dummy_user = AppUser(
            id=10,
            email="member@example.com",
            password_hash="$2b$12$hashedpwd",
            experience=Experience.CUSTOMER,
            status=AppUserStatus.ACTIVE,
        )

        self.dummy_member = Member(
            id=100,
            user_id=10,
            org_id=5,
            email="member@example.com",
            first_name="Alice",
            last_name="Smith",
            status=MemberStatus.ORG_ACTIVE,
        )

        self.dummy_operator_user = AppUser(
            id=20,
            email="ops@example.com",
            password_hash="$2b$12$hashedpwd",
            experience=Experience.OPERATIONS,
            status=AppUserStatus.ACTIVE,
        )

        self.dummy_operator = Operator(
            id=200,
            user_id=20,
            corporate_email="ops@example.com",
            first_name="Bob",
            last_name="Jones",
            status=OperatorStatus.ACTIVE,
        )


    @pytest.mark.anyio
    async def test_get_user_from_token_customer_success(self) -> None:
        self.mock_token_service.verify_access_token.return_value = 10
        self.mock_user_repo.find_by_id = AsyncMock(return_value=self.dummy_user)
        self.mock_member_repo.find_by_user_id = AsyncMock(return_value=self.dummy_member)
        self.mock_member_repo.find_roles_by_user_id = AsyncMock(return_value=["ADMIN", "MEMBER"])

        current_user = await self.service.get_user_from_token("valid_access_token")

        assert isinstance(current_user, CurrentUser)
        assert current_user.id == 10
        assert current_user.email == "member@example.com"
        assert current_user.experience == Experience.CUSTOMER
        assert current_user.status == AppUserStatus.ACTIVE
        assert current_user.first_name == "Alice"
        assert current_user.last_name == "Smith"
        assert current_user.full_name == "Alice Smith"
        assert current_user.roles == ["ADMIN", "MEMBER"]
        assert current_user.scopes.member_id == 100
        assert current_user.scopes.org_id == 5
        assert current_user.scopes.operator_id is None
        assert current_user.member_id == 100
        assert current_user.org_id == 5
        assert current_user.is_active is True
        assert current_user.is_customer is True
        assert current_user.is_operations is False
        # Sensitive credentials are not exposed
        assert not hasattr(current_user, "password_hash")
        assert not hasattr(current_user, "password")

        self.mock_token_service.verify_access_token.assert_called_once_with("valid_access_token")
        self.mock_user_repo.find_by_id.assert_called_once_with(10)
        self.mock_member_repo.find_by_user_id.assert_called_once_with(10)
        self.mock_member_repo.find_roles_by_user_id.assert_called_once_with(10)


    @pytest.mark.anyio
    async def test_get_user_from_token_operations_success(self) -> None:
        self.mock_token_service.verify_access_token.return_value = 20
        self.mock_user_repo.find_by_id = AsyncMock(return_value=self.dummy_operator_user)
        self.mock_operator_repo.find_by_user_id = AsyncMock(return_value=self.dummy_operator)
        self.mock_operator_repo.find_roles_by_user_id = AsyncMock(return_value=["SUPER_ADMIN"])

        current_user = await self.service.get_user_from_token("valid_ops_token")

        assert isinstance(current_user, CurrentUser)
        assert current_user.id == 20
        assert current_user.email == "ops@example.com"
        assert current_user.experience == Experience.OPERATIONS
        assert current_user.first_name == "Bob"
        assert current_user.last_name == "Jones"
        assert current_user.full_name == "Bob Jones"
        assert current_user.roles == ["SUPER_ADMIN"]
        assert current_user.scopes.operator_id == 200
        assert current_user.operator_id == 200
        assert current_user.scopes.member_id is None
        assert current_user.scopes.org_id is None
        assert current_user.is_operations is True
        assert current_user.is_customer is False

        self.mock_operator_repo.find_by_user_id.assert_called_once_with(20)
        self.mock_operator_repo.find_roles_by_user_id.assert_called_once_with(20)


    @pytest.mark.anyio
    async def test_get_user_from_token_invalid_token_raises(self) -> None:
        self.mock_token_service.verify_access_token.side_effect = InvalidTokenError("Invalid token")

        with pytest.raises(InvalidTokenError):
            await self.service.get_user_from_token("malformed_token")

        self.mock_user_repo.find_by_id.assert_not_called()


    @pytest.mark.anyio
    async def test_get_user_from_token_user_not_found_raises(self) -> None:
        self.mock_token_service.verify_access_token.return_value = 999
        self.mock_user_repo.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(UserNotFoundError, match="User with id 999 does not exist"):
            await self.service.get_user_from_token("valid_token_ghost_user")


    @pytest.mark.anyio
    async def test_get_user_from_token_inactive_user_raises(self) -> None:
        inactive_user = AppUser(
            id=10,
            email="inactive@example.com",
            status=AppUserStatus.SUSPENDED,
            experience=Experience.CUSTOMER,
        )
        self.mock_token_service.verify_access_token.return_value = 10
        self.mock_user_repo.find_by_id = AsyncMock(return_value=inactive_user)

        with pytest.raises(UserNotActiveError, match="status=SUSPENDED"):
            await self.service.get_user_from_token("token_inactive_user")


    @pytest.mark.anyio
    async def test_get_active_user_by_id_success(self) -> None:
        self.mock_user_repo.find_by_id = AsyncMock(return_value=self.dummy_user)
        self.mock_member_repo.find_by_user_id = AsyncMock(return_value=None)
        self.mock_member_repo.find_roles_by_user_id = AsyncMock(return_value=[])

        current_user = await self.service.get_active_user_by_id(10)

        assert current_user.id == 10
        assert current_user.email == "member@example.com"
        assert current_user.first_name is None
        assert current_user.last_name is None
        assert current_user.full_name == ""
        assert current_user.roles == []
        assert current_user.scopes == UserScopes()


    def test_build_current_user_service_factory(self) -> None:
        service = build_current_user_service(self.mock_session)
        assert isinstance(service, CurrentUserService)
        assert service._user_repo.session == self.mock_session
        assert service._member_repo.session == self.mock_session
        assert service._operator_repo.session == self.mock_session

