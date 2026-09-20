from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.model.identity import AppUser, AppUserStatus, Role
from app.model.tenant import (
    Datasource,
    DatasourceApprovalStatus,
    DatasourceCategory,
    DatasourceStatus,
    DatasourceType,
)
from app.repository.base import BaseRepository
from app.repository.identity import AppUserRepository, RoleRepository
from app.repository.tenant import DatasourceRepository


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


def test_app_user_repository():
    """Verify AppUserRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    repo = AppUserRepository(mock_session)

    user = AppUser(id=1, email="admin@example.com", status=AppUserStatus.ACTIVE)

    # 1. find_by_email
    mock_session.scalar.return_value = user
    found = repo.find_by_email("admin@example.com")
    assert found == user
    assert mock_session.scalar.called

    # 2. exists_by_email
    mock_session.scalar.return_value = 1
    assert repo.exists_by_email("admin@example.com") is True

    mock_session.scalar.return_value = None
    assert repo.exists_by_email("notfound@example.com") is False

    # 3. find_all_by_status_in
    mock_session.scalars.return_value.all.return_value = [user]
    active_users = repo.find_all_by_status_in([AppUserStatus.ACTIVE])
    assert active_users == [user]


def test_datasource_repository():
    """Verify DatasourceRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    repo = DatasourceRepository(mock_session)

    ds = Datasource(
        id=1,
        org_id=1,
        name="Orders DB",
        category=DatasourceCategory.DATABASE,
        type=DatasourceType.POSTGRESQL,
        approval_status=DatasourceApprovalStatus.APPROVED,
        status=DatasourceStatus.ACTIVE,
    )

    # 1. find_by_id_and_org
    mock_session.scalar.return_value = ds
    found_by_id = repo.find_by_id_and_org(1, org_id=1)
    assert found_by_id == ds

    # 2. find_all_by_org
    mock_session.scalars.return_value.all.return_value = [ds]
    org_datasources = repo.find_all_by_org(org_id=1, skip=0, limit=10)
    assert org_datasources == [ds]

    # 3. count_by_org
    mock_session.scalar.return_value = 10
    assert repo.count_by_org(org_id=1) == 10

    # 4. delete_by_id_and_org
    mock_session.scalar.return_value = ds
    deleted = repo.delete_by_id_and_org(1, org_id=1)
    assert deleted is True
    mock_session.delete.assert_called_once_with(ds)

    # 5. find_by_name_and_org
    mock_session.scalar.return_value = ds
    found_by_name = repo.find_by_name_and_org("Orders DB", org_id=1)
    assert found_by_name == ds

    # 6. exists_by_name_and_org
    mock_session.scalar.return_value = 1
    assert repo.exists_by_name_and_org("Orders DB", org_id=1) is True

    # 7. find_active_by_org
    mock_session.scalars.return_value.all.return_value = [ds]
    active_list = repo.find_active_by_org(org_id=1)
    assert active_list == [ds]

    # 8. find_by_approval_status
    mock_session.scalars.return_value.all.return_value = [ds]
    pending_list = repo.find_by_approval_status(org_id=1, approval_status=DatasourceApprovalStatus.APPROVED)
    assert pending_list == [ds]


def test_role_repository():
    """Verify RoleRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    repo = RoleRepository(mock_session)

    role = Role(id=1, name="ADMIN", description="Administrator")

    # 1. find_by_name
    mock_session.scalar.return_value = role
    found = repo.find_by_name("ADMIN")
    assert found == role

    # 2. exists_by_name
    mock_session.scalar.return_value = 1
    assert repo.exists_by_name("ADMIN") is True

    mock_session.scalar.return_value = None
    assert repo.exists_by_name("NON_EXISTENT") is False
