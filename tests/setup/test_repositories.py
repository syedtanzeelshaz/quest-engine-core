from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.model.identity import AppUser, AppUserStatus
from app.repository.base import BaseRepository, Pageable, SortOrder


def test_base_repository_crud():
    """Verify BaseRepository CRUD operations using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    repo = BaseRepository(AppUser, mock_session)

    user = AppUser(id=1, email="test@example.com", status=AppUserStatus.ACTIVE)

    # 1. Save (stage without flush)
    mock_session.merge.return_value = user
    result = repo.save(user)
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_not_called()
    assert result == user

    # 2. Save and flush (stage and flush immediately)
    mock_session.reset_mock()
    mock_session.merge.return_value = user
    result = repo.save_and_flush(user)
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
    assert result == user

    # 3. Save all (stage sequence without flush, verifies single prefetch query)
    mock_session.reset_mock()
    mock_session.scalars.return_value.all.return_value = [user]
    mock_session.merge.return_value = user
    results = repo.save_all([user])
    mock_session.scalars.assert_called_once()
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_not_called()
    assert results == [user]

    # 4. Save all and flush (stage sequence, prefetch, and flush immediately)
    mock_session.reset_mock()
    mock_session.scalars.return_value.all.return_value = [user]
    mock_session.merge.return_value = user
    results = repo.save_all_and_flush([user])
    mock_session.scalars.assert_called_once()
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
    assert results == [user]

    # 5. Find by ID
    mock_session.reset_mock()
    mock_session.get.return_value = user
    found = repo.find_by_id(1)
    mock_session.get.assert_called_once_with(AppUser, 1)
    assert found == user

    # 6a. Find all (unbounded)
    mock_session.scalars.return_value.all.return_value = [user]
    all_users = repo.find_all()
    assert all_users == [user]

    # 6b. Pageable with default sort (id ASC)
    mock_session.scalars.return_value.all.return_value = [user]
    paged_users = repo.find_all(Pageable(page=0, page_size=10))
    assert paged_users == [user]

    # 6c. Pageable with explicit column sort (AppUser.email DESC)
    mock_session.scalars.return_value.all.return_value = [user]
    paged_sorted = repo.find_all(Pageable(page=0, page_size=10, sort_by=AppUser.email, sort_order=SortOrder.DESC))
    assert paged_sorted == [user]

    # 7. Count
    mock_session.scalar.return_value = 42
    assert repo.count() == 42

    # 8. Delete
    mock_session.reset_mock()
    repo.delete(user)
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 9. Delete by ID
    mock_session.reset_mock()
    mock_session.get.return_value = user
    deleted = repo.delete_by_id(1)
    assert deleted is True
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 10. Delete all
    mock_session.reset_mock()
    repo.delete_all([user])
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 11. Delete all by IDs
    mock_session.reset_mock()
    mock_session.scalars.return_value.all.return_value = [user]
    deleted_count = repo.delete_all_by_ids([1])
    assert deleted_count == 1
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
