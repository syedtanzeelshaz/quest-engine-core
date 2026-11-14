"""
Migration: seed initial permission strings
Revision ID: 2988caad7af3
Revises: 9533672eb915
Create Date: 2026-11-14 15:14:39.518945+00:00
"""
from alembic import op

# revision identifiers
revision = '2988caad7af3'
down_revision = '9533672eb915'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Seed Canonical Permission Strings with Envers Audit Logging
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
                -- Customer Permissions (System seeded: created_by = -1, updated_by = -1)
                ('view.customer.user', 'CUSTOMER', 'View app user information', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('view.customer.member', 'CUSTOMER', 'View customer member information', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('update.customer.member', 'CUSTOMER', 'Update customer member information', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('manage.customer.join-request', 'CUSTOMER', 'Manage organization workspace join requests and invitations', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('view.customer.organization', 'CUSTOMER', 'View organization workspace details and settings', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('create.customer.organization', 'CUSTOMER', 'Create a new tenant organization workspace', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('update.customer.organization', 'CUSTOMER', 'Update organization workspace settings', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('view.customer.organization.role', 'CUSTOMER', 'View roles within organization', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),

                -- Operations Permissions (System seeded: created_by = -1, updated_by = -1)
                ('view.operations.user', 'OPERATIONS', 'View app user information from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('view.operations.member', 'OPERATIONS', 'View tenant organization members from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('update.operations.member', 'OPERATIONS', 'Update tenant organization members from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('manage.operations.join-request', 'OPERATIONS', 'Manage tenant organization join requests and invitations from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('view.operations.organization', 'OPERATIONS', 'View any tenant organization workspace from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('create.operations.organization', 'OPERATIONS', 'Create tenant organization workspaces from operations portal', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('update.operations.organization', 'OPERATIONS', 'Modify tenant organization settings on behalf of a tenant', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('manage.operations.operator', 'OPERATIONS', 'View and manage internal platform operations teammates', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('create.operations.operator', 'OPERATIONS', 'Create internal operator accounts', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('update.operations.operator', 'OPERATIONS', 'Update internal operator status or department', CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1)
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
