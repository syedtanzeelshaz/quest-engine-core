from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_login_service
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import InvalidCredentialsError, UserNotActiveError
from app.main import app
from app.model.identity.app_user import AppUser, AppUserStatus
from app.service.authentication.models import AuthTokenPair


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


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
