import pytest

from app.service.authentication.password import PasswordService


class TestPasswordService:
    @pytest.fixture(autouse=True)
    def setup_service(self) -> None:
        self.service = PasswordService()

    @pytest.mark.anyio
    async def test_hash_creates_valid_bcrypt_hash(self) -> None:
        raw_password = "SecurePassword123!"
        hashed = await self.service.hash(raw_password)

        assert isinstance(hashed, str)
        assert hashed != raw_password
        assert hashed.startswith(("$2b$", "$2a$"))

    @pytest.mark.anyio
    async def test_hash_generates_unique_salts(self) -> None:
        raw_password = "SecurePassword123!"
        hash1 = await self.service.hash(raw_password)
        hash2 = await self.service.hash(raw_password)

        assert hash1 != hash2

    @pytest.mark.anyio
    async def test_verify_returns_true_for_matching_password(self) -> None:
        raw_password = "CorrectHorseBatteryStaple"
        hashed = await self.service.hash(raw_password)

        assert await self.service.verify(raw_password, hashed) is True

    @pytest.mark.anyio
    async def test_verify_returns_false_for_wrong_password(self) -> None:
        raw_password = "CorrectHorseBatteryStaple"
        hashed = await self.service.hash(raw_password)

        assert await self.service.verify("WrongPassword", hashed) is False

    @pytest.mark.anyio
    async def test_verify_returns_false_for_malformed_hash(self) -> None:
        assert await self.service.verify("password", "invalid_not_a_bcrypt_hash") is False
        assert await self.service.verify("password", "") is False
