from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import (
    get_current_user,
    get_login_service,
    get_registration_service,
    get_token_refresh_service,
)
from app.core.primitives.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotActiveError,
)
from app.core.primitives.enums import Experience
from app.main import app
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.member import Member, MemberStatus
from app.service.authentication.models import AuthTokenPair


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuthRegisterRoute:
    def test_register_success_returns_201(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_user = AppUser(
            id=1,
            email="test@example.com",
            experience=Experience.CUSTOMER,
            status=AppUserStatus.ACTIVE,
        )
        dummy_member = Member(
            id=1,
            user_id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            status=MemberStatus.INDIVIDUAL,
        )
        dummy_tokens = AuthTokenPair(
            access_token="acc_token",
            refresh_token="ref_token",
            expires_in=900,
        )
        mock_service.register = AsyncMock(return_value=(dummy_user, dummy_member, dummy_tokens))
        app.dependency_overrides[get_registration_service] = lambda: mock_service

        payload = {
            "email": "test@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["user_id"] == 1
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["experience"] == "CUSTOMER"
        assert data["tokens"]["access_token"] == "acc_token"
        assert data["tokens"]["refresh_token"] == "ref_token"


    def test_register_with_operations_header_passes_to_service(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_user = AppUser(
            id=2,
            email="ops@example.com",
            experience=Experience.OPERATIONS,
            status=AppUserStatus.ACTIVE,
        )
        dummy_operator = MagicMock()
        dummy_operator.first_name = "Jane"
        dummy_operator.last_name = "Admin"
        dummy_tokens = AuthTokenPair(
            access_token="acc_token_ops",
            refresh_token="ref_token_ops",
            expires_in=900,
        )
        mock_service.register = AsyncMock(return_value=(dummy_user, dummy_operator, dummy_tokens))
        app.dependency_overrides[get_registration_service] = lambda: mock_service

        payload = {
            "email": "ops@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "Jane",
            "last_name": "Admin",
        }
        response = client.post(
            "/api/v1/auth/register",
            json=payload,
            headers={"X-Experience": "OPERATIONS"},
        )

        assert response.status_code == HttpCode._201
        called_command = mock_service.register.call_args[0][0]
        assert called_command.experience == Experience.OPERATIONS


    def test_register_with_experience_header_without_x_prefix(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_user = AppUser(
            id=3,
            email="ops2@example.com",
            experience=Experience.OPERATIONS,
            status=AppUserStatus.ACTIVE,
        )
        dummy_operator = MagicMock()
        dummy_operator.first_name = "Jane"
        dummy_operator.last_name = "Admin"
        dummy_tokens = AuthTokenPair(
            access_token="acc_token_ops",
            refresh_token="ref_token_ops",
            expires_in=900,
        )
        mock_service.register = AsyncMock(return_value=(dummy_user, dummy_operator, dummy_tokens))
        app.dependency_overrides[get_registration_service] = lambda: mock_service

        payload = {
            "email": "ops2@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "Jane",
            "last_name": "Admin",
        }
        response = client.post(
            "/api/v1/auth/register",
            json=payload,
            headers={"EXPERIENCE": "OPERATIONS"},
        )

        assert response.status_code == HttpCode._201
        called_command = mock_service.register.call_args[0][0]
        assert called_command.experience == Experience.OPERATIONS


    def test_register_duplicate_email_returns_409(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.register = AsyncMock(side_effect=EmailAlreadyExistsError("Email exists"))
        app.dependency_overrides[get_registration_service] = lambda: mock_service

        payload = {
            "email": "existing@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._409
        assert response.json()["detail"] == HttpMessage.EMAIL_ALREADY_REGISTERED


    def test_register_invalid_email_format_returns_422(self, client: TestClient) -> None:
        payload = {
            "email": "not-an-email",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422


    def test_register_password_mismatch_returns_422(self, client: TestClient) -> None:
        payload = {
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword456!",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422
        assert "Passwords do not match" in response.text
        # Verify plaintext passwords are NEVER present anywhere in the 422 error response
        assert "Password123!" not in response.text
        assert "DifferentPassword456!" not in response.text
        # Verify 'input' field is stripped from all validation errors
        for error in response.json()["detail"]:
            assert "input" not in error


    def test_register_missing_confirm_password_returns_422(self, client: TestClient) -> None:
        payload = {
            "email": "missing@example.com",
            "password": "Password123!",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422

    @pytest.mark.parametrize(
        ("invalid_password", "expected_msg_fragment"),
        [
            ("Short1!", "at least 8 characters long"),
            ("A" * 65 + "1!a", "cannot exceed 64 characters"),
            ("password123!", "at least one uppercase letter"),
            ("PASSWORD123!", "at least one lowercase letter"),
            ("Password!!!!", "at least one digit"),
            ("Password1234", "at least one special character"),
        ],
    )
    def test_register_password_complexity_validations(
        self, client: TestClient, invalid_password: str, expected_msg_fragment: str
    ) -> None:
        payload = {
            "email": "complexity@example.com",
            "password": invalid_password,
            "confirm_password": invalid_password,
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422
        assert expected_msg_fragment in response.text

    @pytest.mark.parametrize("field_name", ["first_name", "last_name"])
    def test_register_name_exceeding_100_chars_returns_422(
        self, client: TestClient, field_name: str
    ) -> None:
        payload = {
            "email": "namelimit@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        payload[field_name] = "A" * 101
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422
        assert "cannot exceed 100 characters" in response.text


class TestAuthLoginRoute:
    def test_login_success_returns_200(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_user = AppUser(id=1, email="user@example.com", status=AppUserStatus.ACTIVE)
        dummy_tokens = AuthTokenPair(access_token="acc", refresh_token="ref", expires_in=900)
        mock_service.authenticate = AsyncMock(return_value=(dummy_user, dummy_tokens))
        app.dependency_overrides[get_login_service] = lambda: mock_service

        payload = {"email": "user@example.com", "password": "validpassword"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._200
        data = response.json()
        assert data["access_token"] == "acc"
        assert data["refresh_token"] == "ref"


    def test_login_with_explicit_experience_passes_to_service(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_user = AppUser(id=2, email="ops@example.com", experience=Experience.OPERATIONS, status=AppUserStatus.ACTIVE)
        dummy_tokens = AuthTokenPair(access_token="ops_acc", refresh_token="ops_ref", expires_in=900)
        mock_service.authenticate = AsyncMock(return_value=(dummy_user, dummy_tokens))
        app.dependency_overrides[get_login_service] = lambda: mock_service

        payload = {
            "email": "ops@example.com",
            "password": "validpassword",
        }
        response = client.post(
            "/api/v1/auth/login",
            json=payload,
            headers={"X-Experience": "OPERATIONS"},
        )

        assert response.status_code == HttpCode._200
        data = response.json()
        assert data["access_token"] == "ops_acc"
        # Verify LoginCommand was called with experience=OPERATIONS from header
        called_command = mock_service.authenticate.call_args[0][0]
        assert called_command.experience == Experience.OPERATIONS


    def test_login_with_invalid_experience_header_returns_400(self, client: TestClient) -> None:
        payload = {"email": "user@example.com", "password": "validpassword"}
        response = client.post(
            "/api/v1/auth/login",
            json=payload,
            headers={"X-Experience": "INVALID_EXP"},
        )

        assert response.status_code == HttpCode._400


    def test_login_invalid_credentials_returns_401(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.authenticate = AsyncMock(side_effect=InvalidCredentialsError("Invalid credentials"))
        app.dependency_overrides[get_login_service] = lambda: mock_service

        payload = {"email": "user@example.com", "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._401
        assert response.json()["detail"] == HttpMessage.INVALID_CREDENTIALS


    def test_login_inactive_account_returns_403(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.authenticate = AsyncMock(side_effect=UserNotActiveError("Not active"))
        app.dependency_overrides[get_login_service] = lambda: mock_service

        payload = {"email": "user@example.com", "password": "password"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._403
        assert response.json()["detail"] == HttpMessage.ACCOUNT_NOT_ACTIVE


class TestAuthRefreshRoute:
    def test_refresh_success_returns_200(self, client: TestClient) -> None:
        mock_service = MagicMock()
        dummy_tokens = AuthTokenPair(access_token="new_acc", refresh_token="new_ref", expires_in=900)
        mock_service.refresh = AsyncMock(return_value=dummy_tokens)
        app.dependency_overrides[get_token_refresh_service] = lambda: mock_service

        payload = {"refresh_token": "valid_refresh_token"}
        response = client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == HttpCode._200
        data = response.json()
        assert data["access_token"] == "new_acc"
        assert data["refresh_token"] == "new_ref"


    def test_refresh_invalid_token_returns_401(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.refresh = AsyncMock(side_effect=InvalidRefreshTokenError("Invalid or expired"))
        app.dependency_overrides[get_token_refresh_service] = lambda: mock_service

        payload = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == HttpCode._401
        assert response.json()["detail"] == HttpMessage.INVALID_REFRESH_TOKEN


class TestAuthLogoutRoute:
    def test_logout_success_returns_200(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.revoke = AsyncMock(return_value=None)
        app.dependency_overrides[get_token_refresh_service] = lambda: mock_service

        dummy_current_user = AppUser(id=1, email="user@example.com", status=AppUserStatus.ACTIVE)
        app.dependency_overrides[get_current_user] = lambda: dummy_current_user

        payload = {"refresh_token": "token_to_revoke"}
        response = client.post("/api/v1/auth/logout", json=payload)

        assert response.status_code == HttpCode._200
        assert response.json()["message"] == HttpMessage.LOGOUT_SUCCESSFUL
        mock_service.revoke.assert_called_once_with("token_to_revoke", requesting_user_id=1)


    def test_logout_unauthenticated_returns_401(self, client: TestClient) -> None:
        # Without overriding get_current_user or providing Authorization header
        payload = {"refresh_token": "token_to_revoke"}
        response = client.post("/api/v1/auth/logout", json=payload)

        assert response.status_code == HttpCode._401
