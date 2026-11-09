"""
Migration: create fresh identity schema and seed roles
Revision ID: 4dfa0d389005
Revises: ce6b11613008
Create Date: 2026-11-09 17:52:50.899641+00:00
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = '4dfa0d389005'
down_revision = 'ce6b11613008'
branch_labels = None
depends_on = None

# author metadata
author_name = 'syedtanzeelshaz'
author_email = 'syedtanzeelshaz@gmail.com'


def upgrade() -> None:
    # Note: identity schema, revinfo, and organization already exist and are intact!

    # -------------------------------------------------------------------------
    # 1. app_user (Pure Security / Authentication Principal)
    # -------------------------------------------------------------------------
    op.create_table(
        "app_user",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("experience", sa.String(50), nullable=True),  # 'CUSTOMER' | 'OPERATIONS'
        sa.Column("status", sa.String(50), nullable=True),      # 'ACTIVE' | 'SUSPENDED' | 'DELETED'
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )

    op.create_table(
        "app_user_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("experience", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 2. refresh_token (Auth Sessions)
    # -------------------------------------------------------------------------
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("identity.app_user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )
    op.create_index("idx_refresh_token_user_id", "refresh_token", ["user_id"], schema="identity")

    # -------------------------------------------------------------------------
    # 3. role (Unified Catalog: Customer & Operations)
    # -------------------------------------------------------------------------
    op.create_table(
        "role",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("experience", sa.String(50), nullable=True),  # 'CUSTOMER' | 'OPERATIONS'
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )

    op.create_table(
        "role_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("name", sa.String(50), nullable=True),
        sa.Column("experience", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 4. member (Customer Persona & User Profile)
    # -------------------------------------------------------------------------
    op.create_table(
        "member",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("identity.app_user.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("identity.organization.id", ondelete="SET NULL"), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),      # 'INDIVIDUAL' | 'ORG_ACTIVE' | 'ORG_SUSPENDED' | 'ORG_OFFBOARDED'
        sa.Column("joined_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )

    op.create_index(
        "uq_member_org_email",
        "member",
        ["org_id", "email"],
        unique=True,
        postgresql_where=sa.text("org_id IS NOT NULL"),
        schema="identity",
    )

    op.create_table(
        "member_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("org_id", sa.BigInteger(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("joined_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 5. member_role (Customer Multi-Role Junction)
    # -------------------------------------------------------------------------
    op.create_table(
        "member_role",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("member_id", sa.BigInteger(), sa.ForeignKey("identity.member.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("identity.role.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.UniqueConstraint("member_id", "role_id", name="uq_member_role"),
        schema="identity",
    )

    op.create_table(
        "member_role_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("member_id", sa.BigInteger(), nullable=True),
        sa.Column("role_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 6. operator (Internal Platform Operations Persona)
    # -------------------------------------------------------------------------
    op.create_table(
        "operator",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("identity.app_user.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("corporate_email", sa.String(255), unique=True, nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),      # 'INVITED' | 'ACTIVE' | 'SUSPENDED' | 'OFFBOARDED'
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )

    op.create_table(
        "operator_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("corporate_email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 7. operator_role (Operations Multi-Role Junction)
    # -------------------------------------------------------------------------
    op.create_table(
        "operator_role",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("operator_id", sa.BigInteger(), sa.ForeignKey("identity.operator.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.BigInteger(), sa.ForeignKey("identity.role.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.UniqueConstraint("operator_id", "role_id", name="uq_operator_role"),
        schema="identity",
    )

    op.create_table(
        "operator_role_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("operator_id", sa.BigInteger(), nullable=True),
        sa.Column("role_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 8. join_request (Invitation & Pre-Registration Staging)
    # -------------------------------------------------------------------------
    op.create_table(
        "join_request",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("org_id", sa.BigInteger(), sa.ForeignKey("identity.organization.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("member_id", sa.BigInteger(), sa.ForeignKey("identity.member.id", ondelete="CASCADE"), nullable=True),
        sa.Column("initiator_member_id", sa.BigInteger(), sa.ForeignKey("identity.member.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type", sa.String(50), nullable=True),        # 'INVITATION' | 'USER_REQUEST'
        sa.Column("status", sa.String(50), nullable=True),      # 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'AUTO_CANCELLED' | 'CANCELLED'
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("reviewed_by_member_id", sa.BigInteger(), sa.ForeignKey("identity.member.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        schema="identity",
    )

    op.create_index(
        "uq_pending_org_invite",
        "join_request",
        ["org_id", "email"],
        unique=True,
        postgresql_where=sa.text("status = 'PENDING'"),
        schema="identity",
    )

    op.create_table(
        "join_request_aud",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("rev", sa.BigInteger(), nullable=False),
        sa.Column("revtype", sa.SmallInteger(), nullable=True),
        sa.Column("org_id", sa.BigInteger(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("member_id", sa.BigInteger(), nullable=True),
        sa.Column("initiator_member_id", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("reviewed_by_member_id", sa.BigInteger(), nullable=True),
        sa.Column("reviewed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", "rev"),
        schema="identity",
    )

    # -------------------------------------------------------------------------
    # 9. Re-link tenant.datasource.reviewed_by -> identity.member(id)
    # -------------------------------------------------------------------------
    op.create_foreign_key(
        "fk_datasource_reviewed_by_member",
        "datasource",
        "member",
        ["reviewed_by"],
        ["id"],
        source_schema="tenant",
        referent_schema="identity",
        ondelete="SET NULL",
    )

    # -------------------------------------------------------------------------
    # 10. Seed Canonical Roles (Customer + Operations) with Audit Revision
    # -------------------------------------------------------------------------
    op.execute("""
        WITH new_revision AS (
            INSERT INTO identity.revinfo (revtstmp)
            VALUES ((FLOOR(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000))::BIGINT)
            RETURNING rev
        ),
        new_roles AS (
            INSERT INTO identity.role (
                name,
                experience,
                description,
                created_at,
                created_by,
                updated_at,
                updated_by
            )
            VALUES
                -- Customer Roles (System seeded: created_by = -1, updated_by = -1)
                ('SUPER_ADMIN', 'CUSTOMER', 'Complete administrative ownership over organization, members, and datasources',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('ADMIN', 'CUSTOMER', 'Organization management, agent configuration, and member administration',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('STAFF', 'CUSTOMER', 'Standard organization member; interacts with assigned AI agents and datasources',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),

                -- Operations Roles (System seeded: created_by = -1, updated_by = -1)
                ('OPERATIONS_ADMIN', 'OPERATIONS', 'Full internal platform administration, audit logs, and system config',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('TECH_OPS', 'OPERATIONS', 'Technical operations, datasource connector diagnostics, and health monitoring',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('SUPPORT_ENGINEER', 'OPERATIONS', 'Customer support, evaluation reviews, and non-sensitive query troubleshooting',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1),
                ('ACCOUNT_EXECUTIVE', 'OPERATIONS', 'Customer onboarding support and usage monitoring',
                 CURRENT_TIMESTAMP, -1, CURRENT_TIMESTAMP, -1)
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
        INSERT INTO identity.role_aud (
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
            role.id,
            revision.rev,
            0,
            role.name,
            role.experience,
            role.description,
            role.created_at,
            role.created_by,
            role.updated_at,
            role.updated_by
        FROM new_roles role
        CROSS JOIN new_revision revision;
    """)


def downgrade() -> None:
    pass