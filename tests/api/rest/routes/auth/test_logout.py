from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_current_user, get_token_refresh_service
from app.core.primitives.enums import Experience
from app.main import app
from app.model.identity.app_user import AppUserStatus
from app.service.user.models import CurrentUser


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuthLogoutRoute:
    def test_logout_success_returns_200(self, client: TestClient) -> None:
        mock_service = MagicMock()
        mock_service.revoke = AsyncMock(return_value=None)
        app.dependency_overrides[get_token_refresh_service] = lambda: mock_service

        dummy_current_user = CurrentUser(
            id=1,
            email="user@example.com",
            experience=Experience.CUSTOMER,
            status=AppUserStatus.ACTIVE,
        )
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
