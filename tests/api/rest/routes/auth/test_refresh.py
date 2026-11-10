from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_token_refresh_service
from app.core.primitives.exceptions import InvalidRefreshTokenError
from app.main import app
from app.service.authentication.models import AuthTokenPair


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


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
