"""
Migration: drop legacy identity tables and btree_gist extension
Revision ID: ce6b11613008
Revises: 925403be8302
Create Date: 2026-11-09 17:49:15.722890+00:00
"""
from alembic import op

# revision identifiers
revision = 'ce6b11613008'
down_revision = '925403be8302'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # 1. Drop obsolete extension used solely for legacy exclusion constraint
    op.execute("DROP EXTENSION IF EXISTS btree_gist CASCADE;")

    # 2. Drop legacy membership, join request, auth & role tables
    # Note: identity.organization and identity.revinfo are preserved to maintain tenant FK integrity!
    op.execute("DROP TABLE IF EXISTS identity.organization_member_aud CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.organization_member CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.join_request_aud CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.join_request CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.refresh_token CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.app_user_aud CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.app_user CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.role_aud CASCADE;")
    op.execute("DROP TABLE IF EXISTS identity.role CASCADE;")


def downgrade() -> None:
    pass