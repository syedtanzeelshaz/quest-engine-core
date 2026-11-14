"""
Migration: seed initial role permission mappings
Revision ID: 397974ed490f
Revises: 0284b4907cc9
Create Date: 2026-11-14 15:52:56.533961+00:00
"""
from alembic import op

# revision identifiers
revision = '397974ed490f'
down_revision = '0284b4907cc9'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Seed Role-to-Permission Mappings with Envers Audit Logging
    # -------------------------------------------------------------------------
    op.execute("""
        WITH new_revision AS (
            INSERT INTO identity.revinfo (revtstmp)
            VALUES ((FLOOR(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000))::BIGINT)
            RETURNING rev
        ),
        mapping_data (role_name, role_experience, perm_name) AS (
            VALUES
                -- Customer: SUPER_ADMIN
                ('SUPER_ADMIN', 'CUSTOMER', '*.customer.**'),

                -- Customer: ADMIN
                ('ADMIN', 'CUSTOMER', 'view.customer.user'),
                ('ADMIN', 'CUSTOMER', 'view.customer.member'),
                ('ADMIN', 'CUSTOMER', 'update.customer.member'),
                ('ADMIN', 'CUSTOMER', 'manage.customer.join-request'),
                ('ADMIN', 'CUSTOMER', 'view.customer.organization'),
                ('ADMIN', 'CUSTOMER', 'update.customer.organization'),
                ('ADMIN', 'CUSTOMER', 'view.customer.organization.role'),

                -- Customer: STAFF
                ('STAFF', 'CUSTOMER', 'view.customer.user'),
                ('STAFF', 'CUSTOMER', 'view.customer.member'),
                ('STAFF', 'CUSTOMER', 'update.customer.member'),
                ('STAFF', 'CUSTOMER', 'view.customer.organization'),

                -- Operations: OPERATIONS_ADMIN
                ('OPERATIONS_ADMIN', 'OPERATIONS', '*.operations.**'),

                -- Operations: TECH_OPS
                ('TECH_OPS', 'OPERATIONS', 'view.operations.user'),
                ('TECH_OPS', 'OPERATIONS', 'view.operations.organization'),
                ('TECH_OPS', 'OPERATIONS', 'view.operations.member'),
                ('TECH_OPS', 'OPERATIONS', 'update.operations.organization'),

                -- Operations: SUPPORT_ENGINEER
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'view.operations.user'),
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'view.operations.organization'),
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'view.operations.member'),
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'update.operations.member'),
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'manage.operations.join-request'),

                -- Operations: ACCOUNT_EXECUTIVE
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'view.operations.organization'),
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'create.operations.organization'),
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'update.operations.organization'),
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'view.operations.member'),
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'manage.operations.join-request')
        ),
        new_mappings AS (
            INSERT INTO identity.role_permission (
                role_id,
                permission_id,
                created_at,
                created_by,
                updated_at,
                updated_by
            )
            SELECT
                r.id,
                p.id,
                CURRENT_TIMESTAMP,
                -1,
                CURRENT_TIMESTAMP,
                -1
            FROM mapping_data m
            JOIN identity.role r ON r.name = m.role_name AND r.experience = m.role_experience
            JOIN identity.permission p ON p.name = m.perm_name AND p.experience = m.role_experience
            RETURNING
                role_id,
                permission_id,
                created_at,
                created_by,
                updated_at,
                updated_by
        )
        INSERT INTO identity.role_permission_aud (
            role_id,
            permission_id,
            rev,
            revtype,
            created_at,
            created_by,
            updated_at,
            updated_by
        )
        SELECT
            nm.role_id,
            nm.permission_id,
            nr.rev,
            0, -- Revtype 0: ADD
            nm.created_at,
            nm.created_by,
            nm.updated_at,
            nm.updated_by
        FROM new_mappings nm
        CROSS JOIN new_revision nr;
    """)


def downgrade() -> None:
    pass
