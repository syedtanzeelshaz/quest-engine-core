"""create identity schema

Revision ID: 454b72bd6841
Revises: None
Create Date: 2026-09-19 12:02:07.608517+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '454b72bd6841'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schema and extension
    op.execute("CREATE SCHEMA IF NOT EXISTS identity;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # Revinfo
    op.create_table(
        'revinfo',
        sa.Column('rev', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), sa.Identity(), primary_key=True),
        sa.Column('revtstmp', sa.BigInteger(), nullable=False),
        schema='identity'
    )

    # App User
    op.create_table(
        'app_user',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('gender', sa.String(50)),
        sa.Column('country', sa.String(100)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('phone', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='identity'
    )

    op.create_table(
        'app_user_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('email', sa.String(255)),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('gender', sa.String(50)),
        sa.Column('country', sa.String(100)),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('phone', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['identity.revinfo.rev']),
        schema='identity'
    )

    # Organization
    op.create_table(
        'organization',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='identity'
    )

    op.create_table(
        'organization_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('name', sa.String(255)),
        sa.Column('slug', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['identity.revinfo.rev']),
        schema='identity'
    )

    # Role
    op.create_table(
        'role',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='identity'
    )

    op.create_table(
        'role_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('name', sa.String(50)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['identity.revinfo.rev']),
        schema='identity'
    )

    # Organization Member & Exclusion Constraint
    op.create_table(
        'organization_member',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('identity.app_user.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('role_id', sa.BigInteger(), sa.ForeignKey('identity.role.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='identity'
    )

    op.execute("""
               ALTER TABLE identity.organization_member
               ADD CONSTRAINT organization_member_one_org_per_user EXCLUDE USING GIST (
                 user_id WITH =,
                 org_id WITH <>
               );
               """)

    op.create_table(
        'organization_member_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('role_id', sa.BigInteger()),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['identity.revinfo.rev']),
        schema='identity'
    )

    # Join Request
    op.create_table(
        'join_request',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('org_id', sa.BigInteger(), sa.ForeignKey('identity.organization.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('identity.app_user.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('initiator_id', sa.BigInteger(), sa.ForeignKey('identity.app_user.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('reviewed_by', sa.BigInteger(), sa.ForeignKey('identity.app_user.id', ondelete='SET NULL')),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        schema='identity'
    )

    op.create_table(
        'join_request_aud',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('rev', sa.BigInteger(), nullable=False),
        sa.Column('revtype', sa.SmallInteger()),
        sa.Column('org_id', sa.BigInteger()),
        sa.Column('user_id', sa.BigInteger()),
        sa.Column('initiator_id', sa.BigInteger()),
        sa.Column('type', sa.String(50)),
        sa.Column('status', sa.String(50)),
        sa.Column('reviewed_by', sa.BigInteger()),
        sa.Column('reviewed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by', sa.BigInteger()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_by', sa.BigInteger()),
        sa.PrimaryKeyConstraint('id', 'rev'),
        sa.ForeignKeyConstraint(['rev'], ['identity.revinfo.rev']),
        schema='identity'
    )


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS identity CASCADE;")