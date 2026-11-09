"""
Migration: drop tenant datasource reviewed_by foreign key
Revision ID: 925403be8302
Revises: 1bfa4827ddf6
Create Date: 2026-11-09 17:32:01.772789+00:00
"""
from alembic import op

# revision identifiers
revision = '925403be8302'
down_revision = '1bfa4827ddf6'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.drop_constraint(
        "datasource_reviewed_by_fkey",
        "datasource",
        schema="tenant",
        type_="foreignkey",
    )


def downgrade() -> None:
    pass