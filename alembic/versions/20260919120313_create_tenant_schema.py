"""
Migration: create tenant schema
Revision ID: fb89c6b82619
Revises: 454b72bd6841
Create Date: 2026-09-19 12:03:13.769604+00:00
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers
revision = 'fb89c6b82619'
down_revision = '454b72bd6841'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS tenant;")

    # Tenant Revinfo
    op.create_table(
        'revinfo',
        sa.Column('rev', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('revtstmp', sa.BigInteger(), nullable=False),
        schema='tenant'
    )

    # Datasource
    op.create_table(
        'datasource',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('connection_config', JSONB),
        sa.Column('approval_status', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('reviewed_by', sa.BigInteger(), sa.ForeignKey('identity.app_user.id', ondelete='SET NULL')),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.UniqueConstraint('id', 'org_id', name='pk_datasource_id_org'),
        schema='tenant'
    )

    op.create_table(
        'datasource_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('name', sa.String(255)),
        sa.Column('category', sa.String(50)),
        sa.Column('type', sa.String(50)),
        sa.Column('connection_config', JSONB),
        sa.Column('approval_status', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('reviewed_by', sa.BigInteger()),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

    # Agent
    op.create_table(
        'agent',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('system_instructions', sa.Text()),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.UniqueConstraint('id', 'org_id', name='pk_agent_id_org'),
        schema='tenant'
    )

    op.create_table(
        'agent_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('name', sa.String(255)),
        sa.Column('description', sa.Text()),
        sa.Column('system_instructions', sa.Text()),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

    # Agent Datasource Mapping
    op.create_table(
        'agent_datasource',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('agent_id', sa.BigInteger(), nullable=False),
        sa.Column('org_id', sa.BigInteger(), nullable=False),
        sa.Column('datasource_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.ForeignKeyConstraint(['agent_id', 'org_id'], ['tenant.agent.id', 'tenant.agent.org_id'], ondelete='CASCADE', name='fk_agent_datasource_agent'),
        sa.ForeignKeyConstraint(['datasource_id', 'org_id'], ['tenant.datasource.id', 'tenant.datasource.org_id'], ondelete='CASCADE', name='fk_agent_datasource_datasource'),
        sa.UniqueConstraint('agent_id', 'datasource_id', name='uq_agent_datasource'),
        schema='tenant'
    )

    op.create_table(
        'agent_datasource_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('agent_id', sa.BigInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('datasource_id', sa.BigInteger()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

    # Agent Access Policy
    op.create_table(
        'agent_access_policy',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_id', sa.BigInteger(), sa.ForeignKey('tenant.agent.id', ondelete='CASCADE'), nullable=False),
        sa.Column('policy_definition', JSONB, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), server_default='true'),
        sa.Column('priority', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='tenant'
    )

    op.create_table(
        'agent_access_policy_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('agent_id', sa.BigInteger()),
        sa.Column('policy_definition', JSONB),
        sa.Column('is_enabled', sa.Boolean()),
        sa.Column('priority', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

    # Datasource Data Policy
    op.create_table(
        'datasource_data_policy',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('datasource_id', sa.BigInteger(), sa.ForeignKey('tenant.datasource.id', ondelete='CASCADE'), nullable=False),
        sa.Column('policy_definition', JSONB, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='tenant'
    )

    op.create_table(
        'datasource_data_policy_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('datasource_id', sa.BigInteger()),
        sa.Column('policy_definition', JSONB),
        sa.Column('is_enabled', sa.Boolean()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

    # Datasource Schema Object
    op.create_table(
        'datasource_schema_object',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'), nullable=False),
        sa.Column('datasource_id', sa.BigInteger(), sa.ForeignKey('tenant.datasource.id', ondelete='CASCADE'), nullable=False),
        sa.Column('object_type', sa.String(50), nullable=False),
        sa.Column('object_name', sa.String(255), nullable=False),
        sa.Column('metadata_payload', JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='tenant'
    )

    op.create_table(
        'datasource_schema_object_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('datasource_id', sa.BigInteger()),
        sa.Column('object_type', sa.String(50)),
        sa.Column('object_name', sa.String(255)),
        sa.Column('metadata_payload', JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['tenant.revinfo.rev']),
        schema='tenant'
    )

def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS tenant CASCADE;")