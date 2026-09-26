"""
Migration: rename datasource type column to kind
Revision ID: 1bfa4827ddf6
Revises: 9c6f1e96a699
Create Date: 2026-09-26 09:13:17.481631+00:00
"""
from alembic import op

# revision identifiers
revision = '1bfa4827ddf6'
down_revision = '9c6f1e96a699'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.alter_column('datasource', 'type', new_column_name='kind', schema='tenant')
    op.alter_column('datasource_aud', 'type', new_column_name='kind', schema='tenant')


def downgrade() -> None:
    op.alter_column('datasource_aud', 'kind', new_column_name='type', schema='tenant')
    op.alter_column('datasource', 'kind', new_column_name='type', schema='tenant')