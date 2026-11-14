"""
Migration: add permission and role_permission tables
Revision ID: 9533672eb915
Revises: 4dfa0d389005
Create Date: 2026-11-14 14:51:52.876959+00:00
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = '9533672eb915'
down_revision = '4dfa0d389005'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. permission (Fine-grained permission catalog)
    # -------------------------------------------------------------------------
    op.create_table(
        "permission",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("experience", sa.String(50), nullable=False),  # 'CUSTOMER' | 'OPERATIONS'
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )
    op.create_index("idx_permission_name", "permission", ["name"], schema="identity")

    op.create_table(
        "permission_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("experience", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 2. role_permission (Role-to-Permission mapping junction)
    # -------------------------------------------------------------------------
    op.create_table(
        "role_permission",
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        schema="identity",
    )

    op.create_table(
        "role_permission_aud",
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("role_id", "permission_id", "rev"),
        schema="identity",
    )


def downgrade() -> None:
    pass
