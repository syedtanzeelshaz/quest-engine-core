from app.core.audit import AUDIT_REGISTRY
from app.model.identity import (
    AppUser,
    AppUserAud,
    JoinRequest,
    JoinRequestAud,
    Organization,
    OrganizationAud,
    OrganizationMember,
    OrganizationMemberAud,
    Role,
    RoleAud,
)
from app.model.tenant import (
    Agent,
    AgentAccessPolicy,
    AgentAccessPolicyAud,
    AgentAud,
    AgentDatasource,
    AgentDatasourceAud,
    Datasource,
    DatasourceAud,
    DatasourceDataPolicy,
    DatasourceDataPolicyAud,
    DatasourceSchemaObject,
    DatasourceSchemaObjectAud,
)


def test_audit_registry_mappings():
    """Verify that every domain model is registered to its respective audit model."""
    expected_mappings = {
        AppUser: AppUserAud,
        Organization: OrganizationAud,
        Role: RoleAud,
        OrganizationMember: OrganizationMemberAud,
        JoinRequest: JoinRequestAud,
        Datasource: DatasourceAud,
        Agent: AgentAud,
        AgentDatasource: AgentDatasourceAud,
        AgentAccessPolicy: AgentAccessPolicyAud,
        DatasourceDataPolicy: DatasourceDataPolicyAud,
        DatasourceSchemaObject: DatasourceSchemaObjectAud,
    }

    for base_cls, aud_cls in expected_mappings.items():
        assert base_cls in AUDIT_REGISTRY, f"{base_cls.__name__} not in AUDIT_REGISTRY"
        assert AUDIT_REGISTRY[base_cls] == aud_cls, (
            f"{base_cls.__name__} mapped to {AUDIT_REGISTRY[base_cls].__name__}, expected {aud_cls.__name__}"
        )
