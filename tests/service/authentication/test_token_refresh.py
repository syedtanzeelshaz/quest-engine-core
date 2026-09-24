from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import InvalidRefreshTokenError
from app.model.identity.app_user import AppUser, AppUserStatus
from app.model.identity.refresh_token import RefreshToken
from app.repository.identity.app_user_repo import AppUserRepository
from app.repository.identity.organization_member_repo import OrganizationMemberRepository
from app.repository.identity.refresh_token_repo import RefreshTokenRepository
from app.service.authentication.models import AuthTokenPair
from app.service.authentication.token import TokenService
from app.service.authentication.token_refresh import TokenRefreshService


class TestTokenRefreshServiceRefresh:
    @pytest.fixture(autouse=True)
    def setup_service(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session

        self.mock_user_repo = MagicMock(spec=AppUserRepository)
        self.mock_user_repo.session = self.mock_session

        self.mock_refresh_token_repo = MagicMock(spec=RefreshTokenRepository)
        self.mock_refresh_token_repo.session = self.mock_session

        self.mock_token_service = MagicMock(spec=TokenService)
        self.mock_org_member_repo = MagicMock(spec=OrganizationMemberRepository)
        self.mock_org_member_repo.session = self.mock_session

        self.service = TokenRefreshService(
            user_repo=self.mock_user_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            token_service=self.mock_token_service,
            org_member_repo=self.mock_org_member_repo,
        )

        self.dummy_user = AppUser(
            id=7,
            email="refresh@example.com",
            password_hash="$2b$12$hash",
            status=AppUserStatus.ACTIVE,
        )

        self.dummy_stored_token = RefreshToken(
            id=1,
            user_id=7,
            token_hash="old_token_hash",
            expires_at=datetime(2026, 12, 31, tzinfo=timezone.utc),
            is_revoked=False,
        )

        self.dummy_new_tokens = AuthTokenPair(
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            expires_in=900,
        )

    def test_refresh_success_rotates_tokens(self) -> None:
        raw_token = "valid_old_refresh_token"
        self.mock_token_service.verify_refresh_token.return_value = 7
        self.mock_token_service.hash_token.side_effect = lambda t: f"hash_of_{t}"
        self.mock_refresh_token_repo.find_by_token_hash.return_value = self.dummy_stored_token
        self.mock_user_repo.find_by_id.return_value = self.dummy_user
        self.mock_org_member_repo.find_roles_by_user.return_value = ["ENGINEER"]
        self.mock_token_service.issue_pair.return_value = self.dummy_new_tokens
        self.mock_token_service.refresh_token_expires_at.return_value = datetime(2027, 1, 1, tzinfo=timezone.utc)

        result_tokens = self.service.refresh(raw_token)

        assert result_tokens == self.dummy_new_tokens

        # Verify old token was revoked (rotation)
        assert self.dummy_stored_token.is_revoked is True
        assert self.dummy_stored_token.revoked_at is not None

        # Verify new token was issued with user claims
        self.mock_token_service.issue_pair.assert_called_once_with(
            user_id=7,
            email="refresh@example.com",
            first_name=self.dummy_user.first_name,
            last_name=self.dummy_user.last_name,
            roles=["ENGINEER"],
        )

        # Verify new refresh token was persisted
        assert self.mock_refresh_token_repo.save_and_flush.call_count == 2
        new_token_record: RefreshToken = self.mock_refresh_token_repo.save_and_flush.call_args_list[1][0][0]
        assert new_token_record.user_id == 7
        assert new_token_record.token_hash == "hash_of_new_refresh_token"
        assert new_token_record.is_revoked is False

    def test_refresh_token_not_found_or_already_used_raises_error(self) -> None:
        self.mock_token_service.verify_refresh_token.return_value = 7
        self.mock_token_service.hash_token.return_value = "unrecognized_hash"
        self.mock_refresh_token_repo.find_by_token_hash.return_value = None

        with pytest.raises(InvalidRefreshTokenError, match="not found, already used, or expired"):
            self.service.refresh("stale_token")

        self.mock_user_repo.find_by_id.assert_not_called()

    def test_refresh_inactive_user_raises_error(self) -> None:
        self.mock_token_service.verify_refresh_token.return_value = 7
        self.mock_token_service.hash_token.return_value = "valid_hash"
        self.mock_refresh_token_repo.find_by_token_hash.return_value = self.dummy_stored_token

        inactive_user = AppUser(id=7, email="user@example.com", status=AppUserStatus.SUSPENDED)
        self.mock_user_repo.find_by_id.return_value = inactive_user

        with pytest.raises(InvalidRefreshTokenError, match="inactive or not found"):
            self.service.refresh("valid_token")


class TestTokenRefreshServiceRevoke:
    @pytest.fixture(autouse=True)
    def setup_service(self, mock_db_session: MagicMock) -> None:
        self.mock_session = mock_db_session

        self.mock_user_repo = MagicMock(spec=AppUserRepository)
        self.mock_user_repo.session = self.mock_session

        self.mock_refresh_token_repo = MagicMock(spec=RefreshTokenRepository)
        self.mock_refresh_token_repo.session = self.mock_session

        self.mock_token_service = MagicMock(spec=TokenService)
        self.mock_org_member_repo = MagicMock(spec=OrganizationMemberRepository)
        self.mock_org_member_repo.session = self.mock_session

        self.service = TokenRefreshService(
            user_repo=self.mock_user_repo,
            refresh_token_repo=self.mock_refresh_token_repo,
            token_service=self.mock_token_service,
            org_member_repo=self.mock_org_member_repo,
        )

    def test_revoke_active_token_marks_it_revoked(self) -> None:
        token_record = RefreshToken(
            id=10,
            user_id=5,
            token_hash="hash_xyz",
            is_revoked=False,
            expires_at=datetime(2026, 12, 31, tzinfo=timezone.utc),
        )
        self.mock_token_service.hash_token.return_value = "hash_xyz"
        self.mock_refresh_token_repo.find_by_token_hash_any.return_value = token_record

        self.service.revoke(raw_refresh_token="my_token", requesting_user_id=5)

        assert token_record.is_revoked is True
        assert token_record.revoked_at is not None
        self.mock_refresh_token_repo.save_and_flush.assert_called_once_with(token_record)

    def test_revoke_token_belonging_to_another_user_raises_error(self) -> None:
        token_record = RefreshToken(
            id=10,
            user_id=999,  # Belongs to user 999
            token_hash="hash_xyz",
            is_revoked=False,
            expires_at=datetime(2026, 12, 31, tzinfo=timezone.utc),
        )
        self.mock_token_service.hash_token.return_value = "hash_xyz"
        self.mock_refresh_token_repo.find_by_token_hash_any.return_value = token_record

        with pytest.raises(InvalidRefreshTokenError, match="does not belong to the current user"):
            self.service.revoke(raw_refresh_token="my_token", requesting_user_id=5)

        assert token_record.is_revoked is False
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()

    def test_revoke_nonexistent_token_succeeds_idempotently(self) -> None:
        self.mock_token_service.hash_token.return_value = "unknown_hash"
        self.mock_refresh_token_repo.find_by_token_hash_any.return_value = None

        # Should not raise any exception
        self.service.revoke(raw_refresh_token="nonexistent_token", requesting_user_id=5)
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()

    def test_revoke_already_revoked_token_is_idempotent(self) -> None:
        token_record = RefreshToken(
            id=10,
            user_id=5,
            token_hash="hash_xyz",
            is_revoked=True,
            revoked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            expires_at=datetime(2026, 12, 31, tzinfo=timezone.utc),
        )
        self.mock_token_service.hash_token.return_value = "hash_xyz"
        self.mock_refresh_token_repo.find_by_token_hash_any.return_value = token_record

        self.service.revoke(raw_refresh_token="my_token", requesting_user_id=5)

        # Already revoked, so save_and_flush should not be called again
        self.mock_refresh_token_repo.save_and_flush.assert_not_called()
