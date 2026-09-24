from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.identity import AppUser, AppUserStatus
from app.repository.base import BaseRepository, Pageable, SortOrder


@pytest.mark.anyio
async def test_base_repository_crud():
    """Verify BaseRepository CRUD operations using a mocked AsyncSession."""
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BaseRepository(AppUser, mock_session)

    user = AppUser(id=1, email="test@example.com", status=AppUserStatus.ACTIVE)

    scalars_result = MagicMock()
    scalars_result.all.return_value = [user]

    # 1. Save (stage without flush)
    mock_session.merge.return_value = user
    result = await repo.save(user)
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_not_called()
    assert result == user

    # 2. Save and flush (stage and flush immediately)
    mock_session.reset_mock()
    mock_session.merge.return_value = user
    result = await repo.save_and_flush(user)
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
    assert result == user

    # 3. Save all (stage sequence without flush, verifies single prefetch query)
    mock_session.reset_mock()
    mock_session.scalars.return_value = scalars_result
    mock_session.merge.return_value = user
    results = await repo.save_all([user])
    mock_session.scalars.assert_called_once()
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_not_called()
    assert results == [user]

    # 4. Save all and flush (stage sequence, prefetch, and flush immediately)
    mock_session.reset_mock()
    mock_session.scalars.return_value = scalars_result
    mock_session.merge.return_value = user
    results = await repo.save_all_and_flush([user])
    mock_session.scalars.assert_called_once()
    mock_session.merge.assert_called_once_with(user)
    mock_session.flush.assert_called_once()
    assert results == [user]

    # 5. Find by ID
    mock_session.reset_mock()
    mock_session.get.return_value = user
    found = await repo.find_by_id(1)
    mock_session.get.assert_called_once_with(AppUser, 1)
    assert found == user

    # 6a. Find all (unbounded)
    mock_session.scalars.return_value = scalars_result
    all_users = await repo.find_all()
    assert all_users == [user]

    # 6b. Pageable with default sort (id ASC)
    mock_session.scalars.return_value = scalars_result
    paged_users = await repo.find_all(Pageable(page=0, page_size=10))
    assert paged_users == [user]

    # 6c. Pageable with explicit column sort (AppUser.email DESC)
    mock_session.scalars.return_value = scalars_result
    paged_sorted = await repo.find_all(Pageable(page=0, page_size=10, sort_by=AppUser.email, sort_order=SortOrder.DESC))
    assert paged_sorted == [user]

    # 7. Count
    mock_session.scalar.return_value = 42
    assert await repo.count() == 42

    # 8. Delete
    mock_session.reset_mock()
    await repo.delete(user)
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 9. Delete by ID
    mock_session.reset_mock()
    mock_session.get.return_value = user
    deleted = await repo.delete_by_id(1)
    assert deleted is True
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 10. Delete all
    mock_session.reset_mock()
    await repo.delete_all([user])
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()

    # 11. Delete all by IDs
    mock_session.reset_mock()
    mock_session.scalars.return_value = scalars_result
    deleted_count = await repo.delete_all_by_ids([1])
    assert deleted_count == 1
    mock_session.delete.assert_called_once_with(user)
    mock_session.flush.assert_called_once()


@pytest.mark.anyio
async def test_role_repository():
    """Verify RoleRepository queries using AsyncSession."""
    from app.model.identity.role import Role
    from app.repository.identity.role_repo import RoleRepository

    mock_session = AsyncMock(spec=AsyncSession)
    repo = RoleRepository(mock_session)

    role = Role(id=1, name="ADMIN")
    mock_session.scalar.return_value = role

    found = await repo.find_by_name("ADMIN")
    assert found == role

    mock_session.scalar.return_value = 1
    exists = await repo.exists_by_name("ADMIN")
    assert exists is True


@pytest.mark.anyio
async def test_organization_repository():
    """Verify OrganizationRepository queries using AsyncSession."""
    from app.model.identity.organization import Organization, OrgStatus
    from app.repository.identity.organization_repo import OrganizationRepository

    mock_session = AsyncMock(spec=AsyncSession)
    repo = OrganizationRepository(mock_session)

    org = Organization(id=1, name="Acme", slug="acme", status=OrgStatus.ACTIVE)
    mock_session.scalar.return_value = org

    found = await repo.find_by_slug("acme")
    assert found == org

    mock_session.scalar.return_value = 1
    assert await repo.exists_by_slug("acme") is True

    scalars_result = MagicMock()
    scalars_result.all.return_value = [org]
    mock_session.scalars.return_value = scalars_result
    orgs = await repo.find_all_by_status_in([OrgStatus.ACTIVE])
    assert orgs == [org]


@pytest.mark.anyio
async def test_join_request_repository():
    """Verify JoinRequestRepository queries using AsyncSession."""
    from app.model.identity.join_request import JoinRequest, JoinRequestStatus
    from app.repository.identity.join_request_repo import JoinRequestRepository

    mock_session = AsyncMock(spec=AsyncSession)
    repo = JoinRequestRepository(mock_session)

    req = JoinRequest(id=1, user_id=1, org_id=1, status=JoinRequestStatus.PENDING)
    mock_session.scalar.return_value = req

    found = await repo.find_pending_by_user_and_org(1, 1)
    assert found == req

    scalars_result = MagicMock()
    scalars_result.all.return_value = [req]
    mock_session.scalars.return_value = scalars_result

    org_reqs = await repo.find_all_by_org(1)
    assert org_reqs == [req]

    user_reqs = await repo.find_all_by_user(1)
    assert user_reqs == [req]

