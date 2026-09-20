from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.model.identity import AppUser, AppUserStatus
from app.repository.base import BaseRepository


def test_base_repository_crud():
    """Verify BaseRepository CRUD operations using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    repo = BaseRepository(AppUser, mock_session)

    user = AppUser(id=1, email="test@example.com", status=AppUserStatus.ACTIVE)

    # 1. Create
    result = repo.create(user)
    mock_session.add.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
    assert result == user

    # 2. Find by ID
    mock_session.get.return_value = user
    found = repo.find_by_id(1)
    mock_session.get.assert_called_once_with(AppUser, 1)
    assert found == user

    # 3. Find all
    mock_session.scalars.return_value.all.return_value = [user]
    all_users = repo.find_all(skip=0, limit=10)
    assert all_users == [user]

    # 4. Count
    mock_session.scalar.return_value = 42
    assert repo.count() == 42

    # 5. Delete by ID
    mock_session.get.return_value = user
    deleted = repo.delete_by_id(1)
    assert deleted is True
    mock_session.delete.assert_called_once_with(user)
