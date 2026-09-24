from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.refresh_token_repo import RefreshTokenRepository


class TestRefreshTokenRepository:
    @pytest.fixture(autouse=True)
    def setup_repo(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session
        self.repo = RefreshTokenRepository(self.mock_session)

        self.dummy_token = RefreshToken(
            id=1,
            user_id=100,
            token_hash="sample_sha256_hash",
            expires_at=datetime(2026, 12, 31, tzinfo=timezone.utc),
            is_revoked=False,
        )

    def test_find_by_token_hash_executes_scalar_query(self) -> None:
        self.mock_session.scalar.return_value = self.dummy_token

        result = self.repo.find_by_token_hash("sample_sha256_hash")

        self.mock_session.scalar.assert_called_once()
        assert result == self.dummy_token

    def test_find_by_token_hash_any_executes_scalar_query(self) -> None:
        self.mock_session.scalar.return_value = self.dummy_token

        result = self.repo.find_by_token_hash_any("sample_sha256_hash")

        self.mock_session.scalar.assert_called_once()
        assert result == self.dummy_token

    def test_find_all_active_by_user_executes_scalars_all(self) -> None:
        self.mock_session.scalars.return_value.all.return_value = [self.dummy_token]

        results = self.repo.find_all_active_by_user(100)

        self.mock_session.scalars.assert_called_once()
        assert results == [self.dummy_token]

    def test_revoke_all_by_user_updates_and_flushes_active_tokens(self) -> None:
        token1 = RefreshToken(id=1, user_id=100, token_hash="hash1", is_revoked=False)
        token2 = RefreshToken(id=2, user_id=100, token_hash="hash2", is_revoked=False)
        self.mock_session.scalars.return_value.all.return_value = [token1, token2]

        count = self.repo.revoke_all_by_user(100)

        assert count == 2
        assert token1.is_revoked is True
        assert token1.revoked_at is not None
        assert token2.is_revoked is True
        assert token2.revoked_at is not None
        self.mock_session.flush.assert_called_once()

    def test_revoke_all_by_user_noop_when_no_active_tokens(self) -> None:
        self.mock_session.scalars.return_value.all.return_value = []

        count = self.repo.revoke_all_by_user(100)

        assert count == 0
        self.mock_session.flush.assert_not_called()
