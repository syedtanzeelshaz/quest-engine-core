
"""drop rev foreign key relation from aud tables

Revision ID: 0a41e0b94f43
Revises: 8514f07e822d
Create Date: 2026-09-20 08:59:41.565791+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '0a41e0b94f43'
down_revision = '8514f07e822d'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Drop rev foreign key constraints from identity schema audit tables
    # -------------------------------------------------------------------------
    op.drop_constraint(
        'app_user_aud_rev_fkey',
        'app_user_aud',
        schema='identity',
        type_='foreignkey',
    )
    op.drop_constraint(
        'organization_aud_rev_fkey',
        'organization_aud',
        schema='identity',
        type_='foreignkey',
    )
    op.drop_constraint(
        'role_aud_rev_fkey',
        'role_aud',
        schema='identity',
        type_='foreignkey',
    )
    op.drop_constraint(
        'organization_member_aud_rev_fkey',
        'organization_member_aud',
        schema='identity',
        type_='foreignkey',
    )
    op.drop_constraint(
        'join_request_aud_rev_fkey',
        'join_request_aud',
        schema='identity',
        type_='foreignkey',
    )

    # -------------------------------------------------------------------------
    # Drop rev foreign key constraints from tenant schema audit tables
    # -------------------------------------------------------------------------
    op.drop_constraint(
        'datasource_aud_rev_fkey',
        'datasource_aud',
        schema='tenant',
        type_='foreignkey',
    )
    op.drop_constraint(
        'agent_aud_rev_fkey',
        'agent_aud',
        schema='tenant',
        type_='foreignkey',
    )
    op.drop_constraint(
        'agent_datasource_aud_rev_fkey',
        'agent_datasource_aud',
        schema='tenant',
        type_='foreignkey',
    )
    op.drop_constraint(
        'agent_access_policy_aud_rev_fkey',
        'agent_access_policy_aud',
        schema='tenant',
        type_='foreignkey',
    )
    op.drop_constraint(
        'datasource_data_policy_aud_rev_fkey',
        'datasource_data_policy_aud',
        schema='tenant',
        type_='foreignkey',
    )
    op.drop_constraint(
        'datasource_schema_object_aud_rev_fkey',
        'datasource_schema_object_aud',
        schema='tenant',
        type_='foreignkey',
    )


def downgrade() -> None:
    # Leaving empty because we are not adding the audit rev foreign key constraints back in downgrade migration
    pass