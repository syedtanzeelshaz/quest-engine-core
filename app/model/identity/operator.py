from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    TIMESTAMP,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin
from app.model.identity.app_user import AppUser
from app.model.identity.role import Role


class OperatorStatus(StrEnum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    OFFBOARDED = "OFFBOARDED"


class OperatorAud(Base):
    """Audit table for identity.operator."""
    __tablename__ = "operator_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    corporate_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(OperatorAud)
class Operator(Base, AuditMetadataMixin):
    """Internal platform operations persona entity."""
    __tablename__ = "operator"
    __table_args__ = {"schema": "identity"}

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
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    corporate_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[OperatorStatus | None] = mapped_column(
        SQLEnum(OperatorStatus, native_enum=False, length=50),
        nullable=True,
        default=OperatorStatus.ACTIVE,
    )

    # Relationships
    user: Mapped[AppUser] = relationship("AppUser")
    roles: Mapped[list[Role]] = relationship("Role", secondary="identity.operator_role")
