"""
Migration: seed initial roles
Revision ID: 8514f07e822d
Revises: fb89c6b82619
Create Date: 2026-09-19 17:28:22.419219+00:00
"""
from alembic import op

# revision identifiers
revision = '8514f07e822d'
down_revision = 'fb89c6b82619'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    op.execute("""
        WITH new_revision AS (
            INSERT INTO identity.revinfo (revtstmp)
            VALUES ((FLOOR(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000))::BIGINT)
            RETURNING rev
        ),
        new_roles AS (
            INSERT INTO identity.role (
                name,
                description,
                created_at,
                created_by,
                updated_at,
                updated_by
            )
            VALUES
                ('SUPER_ADMIN', 'Organization super administrator',
                 CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP, NULL),
                ('ADMIN', 'Organization administrator',
                 CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP, NULL),
                ('MEMBER', 'Member',
                 CURRENT_TIMESTAMP, NULL, CURRENT_TIMESTAMP, NULL)
            RETURNING
                id,
                name,
                description,
                created_at,
                created_by,
                updated_at,
                updated_by
        )
        INSERT INTO identity.role_aud (
            id,
            rev,
            revtype,
            name,
            description,
            created_at,
            created_by,
            updated_at,
            updated_by
        )
        SELECT
            role.id,
            revision.rev,
            0,
            role.name,
            role.description,
            role.created_at,
            role.created_by,
            role.updated_at,
            role.updated_by
        FROM new_roles role
        CROSS JOIN new_revision revision;
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM identity.role_aud
        WHERE name IN ('SUPER_ADMIN', 'ADMIN', 'MEMBER');

        DELETE FROM identity.role
        WHERE name IN ('SUPER_ADMIN', 'ADMIN', 'MEMBER');
    """)