from datetime import datetime, timedelta, timezone

from jose import jwt
import pytest

from app.core.config import Settings
from app.core.exceptions import InvalidRefreshTokenError, InvalidTokenError
from app.service.authentication.token import TokenService


class TestTokenServiceIssuePair:
    @pytest.fixture(autouse=True)
    def setup_service(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.service = TokenService(test_settings)

    def test_issue_pair_returns_valid_tokens_and_expiry(self) -> None:
        pair = self.service.issue_pair(
            user_id=42,
            email="developer@example.com",
            first_name="Jane",
            last_name="Doe",
            roles=["ADMIN"],
        )

        assert pair.access_token
        assert pair.refresh_token
        assert pair.expires_in == self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

        # Validate access token claims
        access_payload = jwt.decode(
            pair.access_token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.JWT_ALGORITHM],
        )
        assert access_payload["sub"] == "developer@example.com"
        assert access_payload["type"] == "access"
        assert access_payload["details"]["id"] == 42
        assert access_payload["details"]["firstName"] == "Jane"
        assert access_payload["details"]["lastName"] == "Doe"
        assert access_payload["roles"] == ["ADMIN"]

        # Validate refresh token claims
        refresh_payload = jwt.decode(
            pair.refresh_token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.JWT_ALGORITHM],
        )
        assert refresh_payload["sub"] == "developer@example.com"
        assert refresh_payload["user_id"] == 42
        assert refresh_payload["type"] == "refresh"

    def test_issue_pair_handles_optional_fields_as_empty_or_none(self) -> None:
        pair = self.service.issue_pair(
            user_id=1,
            email="solo@example.com",
            first_name=None,
            last_name=None,
            roles=None,
        )

        access_payload = jwt.decode(
            pair.access_token,
            self.settings.JWT_SECRET_KEY,
            algorithms=[self.settings.JWT_ALGORITHM],
        )
        assert access_payload["details"]["firstName"] == ""
        assert access_payload["details"]["lastName"] == ""
        assert access_payload["roles"] is None


class TestTokenServiceVerifyAccessToken:
    @pytest.fixture(autouse=True)
    def setup_service(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.service = TokenService(test_settings)

    def test_verify_access_token_success(self) -> None:
        pair = self.service.issue_pair(user_id=99, email="user@example.com")
        user_id = self.service.verify_access_token(pair.access_token)

        assert user_id == 99

    def test_verify_access_token_with_expired_token_raises_invalid_token_error(self) -> None:
        expired_payload = {
            "sub": "user@example.com",
            "details": {"id": 99},
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(
            expired_payload,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )

        with pytest.raises(InvalidTokenError, match="Token is invalid or expired"):
            self.service.verify_access_token(expired_token)

    def test_verify_access_token_with_tampered_signature_raises_error(self) -> None:
        pair = self.service.issue_pair(user_id=99, email="user@example.com")
        tampered_token = pair.access_token[:-4] + "abcd"

        with pytest.raises(InvalidTokenError, match="Token is invalid or expired"):
            self.service.verify_access_token(tampered_token)

    def test_verify_access_token_rejects_refresh_token_type(self) -> None:
        pair = self.service.issue_pair(user_id=99, email="user@example.com")

        with pytest.raises(InvalidTokenError, match="Expected token type 'access'"):
            self.service.verify_access_token(pair.refresh_token)


class TestTokenServiceVerifyRefreshToken:
    @pytest.fixture(autouse=True)
    def setup_service(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.service = TokenService(test_settings)

    def test_verify_refresh_token_success(self) -> None:
        pair = self.service.issue_pair(user_id=88, email="user@example.com")
        user_id = self.service.verify_refresh_token(pair.refresh_token)

        assert user_id == 88

    def test_verify_refresh_token_with_expired_token_raises_invalid_refresh_token_error(self) -> None:
        expired_payload = {
            "sub": "user@example.com",
            "user_id": 88,
            "type": "refresh",
            "iat": datetime.now(timezone.utc) - timedelta(days=10),
            "exp": datetime.now(timezone.utc) - timedelta(days=1),
        }
        expired_token = jwt.encode(
            expired_payload,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )

        with pytest.raises(InvalidRefreshTokenError, match="Token is invalid or expired"):
            self.service.verify_refresh_token(expired_token)

    def test_verify_refresh_token_rejects_access_token_type(self) -> None:
        pair = self.service.issue_pair(user_id=88, email="user@example.com")

        with pytest.raises(InvalidRefreshTokenError, match="Expected token type 'refresh'"):
            self.service.verify_refresh_token(pair.access_token)


class TestTokenServiceUtilities:
    @pytest.fixture(autouse=True)
    def setup_service(self, test_settings: Settings) -> None:
        self.settings = test_settings
        self.service = TokenService(test_settings)

    def test_hash_token_produces_consistent_sha256_hex(self) -> None:
        token = "some-random-raw-jwt-string"
        hash1 = self.service.hash_token(token)
        hash2 = self.service.hash_token(token)

        assert hash1 == hash2
        assert len(hash1) == 64
        assert hash1 != token

    def test_decode_token_returns_payload_dict(self) -> None:
        pair = self.service.issue_pair(user_id=10, email="decode@example.com")
        payload = self.service.decode_token(pair.access_token)

        assert payload["sub"] == "decode@example.com"
        assert payload["details"]["id"] == 10

    def test_refresh_token_expires_at_is_in_future(self) -> None:
        now = datetime.now(timezone.utc)
        expires_at = self.service.refresh_token_expires_at()

        assert expires_at > now
        diff_days = (expires_at - now).total_seconds() / 86400
        assert pytest.approx(diff_days, rel=0.05) == self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
