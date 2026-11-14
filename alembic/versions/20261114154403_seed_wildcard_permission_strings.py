"""
Migration: seed wildcard permission strings
Revision ID: 0284b4907cc9
Revises: 2988caad7af3
Create Date: 2026-11-14 15:44:03.036002+00:00
"""
from alembic import op

# revision identifiers
revision = '0284b4907cc9'
down_revision = '2988caad7af3'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Seed Wildcard Permission Strings with Envers Audit Logging
    # -------------------------------------------------------------------------
    op.execute("""
        WITH new_revision AS (
            INSERT INTO identity.revinfo (revtstmp)
            VALUES ((FLOOR(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000))::BIGINT)
            RETURNING rev
        ),
        new_permissions AS (
            INSERT INTO identity.permission (
                name,
                experience,
                description,
                created_at,
                created_by,
                updated_at,
                updated_by
            )
            VALUES
                ('*.customer.**', 'CUSTOMER', 'Full administrative access across all customer workspace domains', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('*.operations.**', 'OPERATIONS', 'Full administrative access across all operations platform domains', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1)
            RETURNING
                id,
                name,
                experience,
                description,
                created_at,
                created_by,
                updated_at,
                updated_by
        )
        INSERT INTO identity.permission_aud (
            id,
            rev,
            revtype,
            name,
            experience,
            description,
            created_at,
            created_by,
            updated_at,
            updated_by
        )
        SELECT
            p.id,
            nr.rev,
            0, -- Revtype 0: ADD
            p.name,
            p.experience,
            p.description,
            p.created_at,
            p.created_by,
            p.updated_at,
            p.updated_by
        FROM new_permissions p
        CROSS JOIN new_revision nr;
    """)


def downgrade() -> None:
    pass
