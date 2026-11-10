from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.rest.constants.http_codes import HttpCode
from app.api.rest.constants.http_messages import HttpMessage
from app.api.rest.deps import get_registration_service
from app.core.primitives.enums import Experience
from app.core.primitives.exceptions import EmailAlreadyExistsError
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
