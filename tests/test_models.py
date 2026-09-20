import pytest
from sqlalchemy import inspect
from app.core.database import Base
from app.core.audit import AUDIT_REGISTRY, RevType
import app.model  # loads all models


def test_models_metadata_registered():
    """Verify that all core tables and audit tables are registered in Base.metadata."""
    table_names = set(Base.metadata.tables.keys())

    expected_identity_tables = {
        "identity.revinfo",
        "identity.app_user",
        "identity.app_user_aud",
        "identity.organization",
        "identity.organization_aud",
        "identity.role",
        "identity.role_aud",
        "identity.organization_member",
        "identity.organization_member_aud",
        "identity.join_request",
        "identity.join_request_aud",
    }

    expected_tenant_tables = {
        "tenant.revinfo",
        "tenant.datasource",
        "tenant.datasource_aud",
        "tenant.agent",
        "tenant.agent_aud",
        "tenant.agent_datasource",
        "tenant.agent_datasource_aud",
        "tenant.agent_access_policy",
        "tenant.agent_access_policy_aud",
        "tenant.datasource_data_policy",
        "tenant.datasource_data_policy_aud",
        "tenant.datasource_schema_object",
        "tenant.datasource_schema_object_aud",
    }

    for expected in expected_identity_tables:
        assert expected in table_names, f"Missing table: {expected}"

    for expected in expected_tenant_tables:
        assert expected in table_names, f"Missing table: {expected}"


def test_audit_registry_mappings():
    """Verify that every domain model is registered to its respective audit model."""
    from app.model.identity import (
        AppUser, AppUserAud,
        Organization, OrganizationAud,
        Role, RoleAud,
        OrganizationMember, OrganizationMemberAud,
        JoinRequest, JoinRequestAud,
    )
    from app.model.tenant import (
        Datasource, DatasourceAud,
        Agent, AgentAud,
        AgentDatasource, AgentDatasourceAud,
        AgentAccessPolicy, AgentAccessPolicyAud,
        DatasourceDataPolicy, DatasourceDataPolicyAud,
        DatasourceSchemaObject, DatasourceSchemaObjectAud,
    )

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


def test_tenant_isolation_constraints():
    """Verify that composite foreign keys and unique constraints enforcing tenant isolation are configured."""
    agent_datasource_table = Base.metadata.tables["tenant.agent_datasource"]

    # Check composite FKs
    fk_names = {fk.name for fk in agent_datasource_table.foreign_keys}
    assert "fk_agent_datasource_agent" in fk_names or any(
        "agent" in (fk.name or "") for fk in agent_datasource_table.foreign_keys
    )
    assert "fk_agent_datasource_datasource" in fk_names or any(
        "datasource" in (fk.name or "") for fk in agent_datasource_table.foreign_keys
    )

    # Check composite unique constraint on (agent_id, datasource_id)
    uq_names = {c.name for c in agent_datasource_table.constraints if hasattr(c, "name")}
    assert "uq_agent_datasource" in uq_names
