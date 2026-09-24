import pytest

from app.service.authentication.password import PasswordService


class TestPasswordService:
    @pytest.fixture(autouse=True)
    def setup_service(self) -> None:
        self.service = PasswordService()

    def test_hash_creates_valid_bcrypt_hash(self) -> None:
        raw_password = "SecurePassword123!"
        hashed = self.service.hash(raw_password)

        assert isinstance(hashed, str)
        assert hashed != raw_password
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_hash_generates_unique_salts(self) -> None:
        raw_password = "SecurePassword123!"
        hash1 = self.service.hash(raw_password)
        hash2 = self.service.hash(raw_password)

        assert hash1 != hash2

    def test_verify_returns_true_for_matching_password(self) -> None:
        raw_password = "CorrectHorseBatteryStaple"
        hashed = self.service.hash(raw_password)

        assert self.service.verify(raw_password, hashed) is True

    def test_verify_returns_false_for_wrong_password(self) -> None:
        raw_password = "CorrectHorseBatteryStaple"
        hashed = self.service.hash(raw_password)

        assert self.service.verify("WrongPassword", hashed) is False

    def test_verify_returns_false_for_malformed_hash(self) -> None:
        assert self.service.verify("password", "invalid_not_a_bcrypt_hash") is False
        assert self.service.verify("password", "") is False
