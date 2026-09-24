from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotActiveError,
)
from app.main import app
from app.model.identity.app_user import AppUser, AppUserStatus
from app.service.authentication.models import AuthTokenPair


@pytest.fixture
def client(mock_db_session: MagicMock) -> TestClient:
    app.dependency_overrides[get_db] = lambda: mock_db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuthRegisterRoute:
    @patch("app.api.rest.routes.auth.RegistrationService")
    def test_register_success_returns_201(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        dummy_user = AppUser(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            status=AppUserStatus.ACTIVE,
        )
        dummy_tokens = AuthTokenPair(
            access_token="acc_token",
            refresh_token="ref_token",
            expires_in=900,
        )
        mock_service.register = AsyncMock(return_value=(dummy_user, dummy_tokens))

        payload = {
            "email": "test@example.com",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["user_id"] == 1
        assert data["tokens"]["access_token"] == "acc_token"
        assert data["tokens"]["refresh_token"] == "ref_token"

    @patch("app.api.rest.routes.auth.RegistrationService")
    def test_register_duplicate_email_returns_409(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        mock_service.register = AsyncMock(side_effect=EmailAlreadyExistsError("Email exists"))

        payload = {
            "email": "existing@example.com",
            "password": "Password123!",
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
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == HttpCode._422


class TestAuthLoginRoute:
    @patch("app.api.rest.routes.auth.LoginService")
    def test_login_success_returns_200(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        dummy_user = AppUser(id=1, email="user@example.com", status=AppUserStatus.ACTIVE)
        dummy_tokens = AuthTokenPair(access_token="acc", refresh_token="ref", expires_in=900)
        mock_service.authenticate = AsyncMock(return_value=(dummy_user, dummy_tokens))

        payload = {"email": "user@example.com", "password": "validpassword"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._200
        data = response.json()
        assert data["access_token"] == "acc"
        assert data["refresh_token"] == "ref"

    @patch("app.api.rest.routes.auth.LoginService")
    def test_login_invalid_credentials_returns_401(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        mock_service.authenticate = AsyncMock(side_effect=InvalidCredentialsError("Invalid credentials"))

        payload = {"email": "user@example.com", "password": "wrongpassword"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._401
        assert response.json()["detail"] == HttpMessage.INVALID_CREDENTIALS

    @patch("app.api.rest.routes.auth.LoginService")
    def test_login_inactive_account_returns_403(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        mock_service.authenticate = AsyncMock(side_effect=UserNotActiveError("Not active"))

        payload = {"email": "user@example.com", "password": "password"}
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == HttpCode._403
        assert response.json()["detail"] == HttpMessage.ACCOUNT_NOT_ACTIVE


class TestAuthRefreshRoute:
    @patch("app.api.rest.routes.auth.TokenRefreshService")
    def test_refresh_success_returns_200(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        dummy_tokens = AuthTokenPair(access_token="new_acc", refresh_token="new_ref", expires_in=900)
        mock_service.refresh = AsyncMock(return_value=dummy_tokens)

        payload = {"refresh_token": "valid_refresh_token"}
        response = client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == HttpCode._200
        data = response.json()
        assert data["access_token"] == "new_acc"
        assert data["refresh_token"] == "new_ref"

    @patch("app.api.rest.routes.auth.TokenRefreshService")
    def test_refresh_invalid_token_returns_401(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        mock_service.refresh = AsyncMock(side_effect=InvalidRefreshTokenError("Invalid or expired"))

        payload = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == HttpCode._401
        assert response.json()["detail"] == HttpMessage.INVALID_REFRESH_TOKEN


class TestAuthLogoutRoute:
    @patch("app.api.rest.routes.auth.TokenRefreshService")
    def test_logout_success_returns_200(self, mock_service_cls: MagicMock, client: TestClient) -> None:
        mock_service = mock_service_cls.return_value
        mock_service.revoke = AsyncMock(return_value=None)

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
