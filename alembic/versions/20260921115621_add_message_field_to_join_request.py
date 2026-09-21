"""
Migration: add message field to join request
Revision ID: 452994c75a9c
Revises: 0a41e0b94f43
Create Date: 2026-09-21 11:56:21.459437+00:00
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = '452994c75a9c'
down_revision = '0a41e0b94f43'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.add_column(
        'join_request',
        sa.Column('message', sa.Text(), nullable=True),
        schema='identity',
    )
    op.add_column(
        'join_request_aud',
        sa.Column('message', sa.Text(), nullable=True),
        schema='identity',
    )


def downgrade() -> None:
    op.drop_column('join_request_aud', 'message', schema='identity')
    op.drop_column('join_request', 'message', schema='identity')