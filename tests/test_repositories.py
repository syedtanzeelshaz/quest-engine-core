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

    # 1. find_all_by_org
    mock_session.scalars.return_value.all.return_value = [ds]
    org_datasources = repo.find_all_by_org(org_id=1, skip=0, limit=10)
    assert org_datasources == [ds]

    # 2. count_by_org
    mock_session.scalar.return_value = 10
    assert repo.count_by_org(org_id=1) == 10

    # 3. find_all_by_name_and_org
    mock_session.scalars.return_value.all.return_value = [ds]
    found_by_name = repo.find_all_by_name_and_org("Orders DB", org_id=1)
    assert found_by_name == [ds]

    # 4. exists_by_name_and_org
    mock_session.scalar.return_value = 1
    assert repo.exists_by_name_and_org("Orders DB", org_id=1) is True

    # 5. find_all_active_by_org
    mock_session.scalars.return_value.all.return_value = [ds]
    active_list = repo.find_all_active_by_org(org_id=1)
    assert active_list == [ds]

    # 6. find_all_by_org_and_approval_status
    mock_session.scalars.return_value.all.return_value = [ds]
    pending_list = repo.find_all_by_org_and_approval_status(
        org_id=1, approval_status=DatasourceApprovalStatus.APPROVED
    )
    assert pending_list == [ds]

    # 7. find_all_by_org_and_status
    mock_session.scalars.return_value.all.return_value = [ds]
    active_status_list = repo.find_all_by_org_and_status(
        org_id=1, status=DatasourceStatus.ACTIVE
    )
    assert active_status_list == [ds]


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


def test_organization_member_repository():
    """Verify OrganizationMemberRepository returns lists for user memberships."""
    mock_session = MagicMock(spec=Session)
    from app.model.identity import OrganizationMember, OrgMemberStatus
    from app.repository.identity import OrganizationMemberRepository

    repo = OrganizationMemberRepository(mock_session)
    member = OrganizationMember(
        id=1, user_id=10, org_id=1, role_id=2, status=OrgMemberStatus.ACTIVE
    )

    mock_session.scalars.return_value.all.return_value = [member]
    memberships = repo.find_all_by_user_and_org(user_id=10, org_id=1)
    assert memberships == [member]

    active_memberships = repo.find_all_active_by_user(user_id=10)
    assert active_memberships == [member]

    org_members = repo.find_all_by_org(org_id=1)
    assert org_members == [member]


def test_join_request_repository():
    """Verify JoinRequestRepository queries without silent filters."""
    mock_session = MagicMock(spec=Session)
    from app.model.identity import JoinRequest, JoinRequestStatus, JoinRequestType
    from app.repository.identity import JoinRequestRepository

    repo = JoinRequestRepository(mock_session)
    req = JoinRequest(
        id=1,
        org_id=1,
        user_id=10,
        initiator_id=10,
        type=JoinRequestType.USER_REQUEST,
        status=JoinRequestStatus.PENDING,
    )

    mock_session.scalar.return_value = req
    pending = repo.find_pending_by_user_and_org(user_id=10, org_id=1)
    assert pending == req

    mock_session.scalars.return_value.all.return_value = [req]
    org_reqs = repo.find_all_by_org(org_id=1)
    assert org_reqs == [req]

    user_reqs = repo.find_all_by_user(user_id=10)
    assert user_reqs == [req]


def test_agent_datasource_repository():
    """Verify AgentDatasourceRepository queries without redundant org_id."""
    mock_session = MagicMock(spec=Session)
    from app.model.tenant import AgentDatasource
    from app.repository.tenant import AgentDatasourceRepository

    repo = AgentDatasourceRepository(mock_session)
    assoc = AgentDatasource(id=1, agent_id=10, datasource_id=20, org_id=1)

    mock_session.scalar.return_value = assoc
    found = repo.find_by_agent_and_datasource(agent_id=10, datasource_id=20)
    assert found == assoc

    mock_session.scalars.return_value.all.return_value = [assoc]
    agent_assocs = repo.find_all_by_agent(agent_id=10)
    assert agent_assocs == [assoc]

    ds_assocs = repo.find_all_by_datasource(datasource_id=20)
    assert ds_assocs == [assoc]


def test_agent_repository():
    """Verify AgentRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    from app.model.tenant.agent import Agent, AgentStatus
    from app.repository.tenant.agent_repo import AgentRepository

    repo = AgentRepository(mock_session)
    agent = Agent(id=1, org_id=1, name="Support Bot", status=AgentStatus.ACTIVE)

    # 1. find_all_by_org
    mock_session.scalars.return_value.all.return_value = [agent]
    agents = repo.find_all_by_org(org_id=1)
    assert agents == [agent]

    # 2. count_by_org
    mock_session.scalar.return_value = 5
    assert repo.count_by_org(org_id=1) == 5

    # 3. find_all_by_name_and_org
    mock_session.scalars.return_value.all.return_value = [agent]
    matching = repo.find_all_by_name_and_org("Support Bot", org_id=1)
    assert matching == [agent]

    # 4. exists_by_name_and_org
    mock_session.scalar.return_value = 1
    assert repo.exists_by_name_and_org("Support Bot", org_id=1) is True

    # 5. find_all_active_by_org
    mock_session.scalars.return_value.all.return_value = [agent]
    active_agents = repo.find_all_active_by_org(org_id=1)
    assert active_agents == [agent]


def test_datasource_schema_object_repository():
    """Verify DatasourceSchemaObjectRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    from app.model.tenant.datasource_schema_object import (
        DatasourceSchemaObject,
        SchemaObjectType,
    )
    from app.repository.tenant.datasource_schema_object_repo import (
        DatasourceSchemaObjectRepository,
    )

    repo = DatasourceSchemaObjectRepository(mock_session)
    obj = DatasourceSchemaObject(
        id=1,
        org_id=1,
        datasource_id=10,
        object_type=SchemaObjectType.TABLE,
        object_name="users",
    )

    # 1. find_all_by_datasource
    mock_session.scalars.return_value.all.return_value = [obj]
    all_objs = repo.find_all_by_datasource(datasource_id=10)
    assert all_objs == [obj]

    # 2. find_all_by_datasource_and_object_name
    mock_session.scalars.return_value.all.return_value = [obj]
    matching = repo.find_all_by_datasource_and_object_name(
        datasource_id=10, object_name="users"
    )
    assert matching == [obj]


def test_agent_access_policy_repository():
    """Verify AgentAccessPolicyRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    from app.model.tenant.agent_access_policy import AgentAccessPolicy
    from app.repository.tenant.agent_access_policy_repo import (
        AgentAccessPolicyRepository,
    )

    repo = AgentAccessPolicyRepository(mock_session)
    policy = AgentAccessPolicy(id=1, agent_id=5, org_id=1)

    mock_session.scalars.return_value.all.return_value = [policy]
    policies = repo.find_all_by_agent(agent_id=5)
    assert policies == [policy]


def test_datasource_data_policy_repository():
    """Verify DatasourceDataPolicyRepository domain methods using a mocked Session."""
    mock_session = MagicMock(spec=Session)
    from app.model.tenant.datasource_data_policy import DatasourceDataPolicy
    from app.repository.tenant.datasource_data_policy_repo import (
        DatasourceDataPolicyRepository,
    )

    repo = DatasourceDataPolicyRepository(mock_session)
    policy = DatasourceDataPolicy(id=1, datasource_id=20, org_id=1)

    mock_session.scalars.return_value.all.return_value = [policy]
    policies = repo.find_all_by_datasource(datasource_id=20)
    assert policies == [policy]
