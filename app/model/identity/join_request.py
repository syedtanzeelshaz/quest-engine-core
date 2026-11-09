from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    Index,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
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
from app.model.identity.member import Member
from app.model.identity.organization import Organization


class JoinRequestType(StrEnum):
    INVITATION = "INVITATION"
    USER_REQUEST = "USER_REQUEST"


class JoinRequestStatus(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AUTO_CANCELLED = "AUTO_CANCELLED"
    CANCELLED = "CANCELLED"


class JoinRequestAud(Base):
    """Audit table for identity.join_request."""
    __tablename__ = "join_request_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    member_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    initiator_member_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_member_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(JoinRequestAud)
class JoinRequest(Base, AuditMetadataMixin):
    """Organization join request or invitation staging entity."""
    __tablename__ = "join_request"
    __table_args__ = (
        Index(
            "uq_pending_org_invite",
            "org_id",
            "email",
            unique=True,
            postgresql_where=text("status = 'PENDING'"),
        ),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    org_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    member_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.member.id", ondelete="CASCADE"),
        nullable=True,
    )
    initiator_member_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.member.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[JoinRequestType | None] = mapped_column(
        SQLEnum(JoinRequestType, native_enum=False, length=50),
        nullable=True,
    )
    status: Mapped[JoinRequestStatus | None] = mapped_column(
        SQLEnum(JoinRequestStatus, native_enum=False, length=50),
        nullable=True,
        default=JoinRequestStatus.PENDING,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_member_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.member.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", lazy="select")
    member: Mapped[Member | None] = relationship("Member", foreign_keys=[member_id], lazy="select")
    initiator_member: Mapped[Member | None] = relationship("Member", foreign_keys=[initiator_member_id], lazy="select")
    reviewed_by_member: Mapped[Member | None] = relationship("Member", foreign_keys=[reviewed_by_member_id], lazy="select")
