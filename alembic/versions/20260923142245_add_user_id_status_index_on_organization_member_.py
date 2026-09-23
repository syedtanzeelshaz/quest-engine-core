"""
Migration: add user-id status index on organization_member table
Revision ID: 9c6f1e96a699
Revises: c732cdf0fc3e
Create Date: 2026-09-23 14:22:45.272758+00:00
"""
from alembic import op

# revision identifiers
revision = '9c6f1e96a699'
down_revision = 'c732cdf0fc3e'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.create_index(
        "idx_organization_member_user_id_status",
        "organization_member",
        ["user_id", "status"],
        schema="identity",
    )


def downgrade() -> None:
    op.drop_index(
        "idx_organization_member_user_id_status",
        table_name="organization_member",
        schema="identity",
    )