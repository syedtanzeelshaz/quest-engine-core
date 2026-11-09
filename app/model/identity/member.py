from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Identity,
    Index,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    TIMESTAMP,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin
from app.model.identity.app_user import AppUser
from app.model.identity.organization import Organization
from app.model.identity.role import Role


class MemberStatus(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    ORG_ACTIVE = "ORG_ACTIVE"
    ORG_SUSPENDED = "ORG_SUSPENDED"
    ORG_OFFBOARDED = "ORG_OFFBOARDED"


class MemberAud(Base):
    """Audit table for identity.member."""
    __tablename__ = "member_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date(), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    joined_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(MemberAud)
class Member(Base, AuditMetadataMixin):
    """Customer persona & personal/workspace profile entity."""
    __tablename__ = "member"
    __table_args__ = (
        Index(
            "uq_member_org_email",
            "org_id",
            "email",
            unique=True,
            postgresql_where=text("org_id IS NOT NULL"),
        ),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    org_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.organization.id", ondelete="SET NULL"),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date(), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[MemberStatus | None] = mapped_column(
        SQLEnum(MemberStatus, native_enum=False, length=50),
        nullable=True,
        default=MemberStatus.INDIVIDUAL,
    )
    joined_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user: Mapped[AppUser] = relationship("AppUser")
    organization: Mapped[Organization | None] = relationship("Organization")
    roles: Mapped[list[Role]] = relationship("Role", secondary="identity.member_role")
