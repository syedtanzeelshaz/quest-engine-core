"""
Migration: add refresh_token table in identity schema
Revision ID: c732cdf0fc3e
Revises: 452994c75a9c
Create Date: 2026-09-22 19:20:13.440161+00:00
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = 'c732cdf0fc3e'
down_revision = '452994c75a9c'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("identity.app_user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_by", sa.BigInteger()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("updated_by", sa.BigInteger()),
        schema="identity",
    )
    
    op.create_index(
        "idx_refresh_token_user_id",
        "refresh_token",
        ["user_id"],
        schema="identity",
    )


def downgrade() -> None:
    op.drop_index("idx_refresh_token_user_id", table_name="refresh_token", schema="identity")
    op.drop_table("refresh_token", schema="identity")