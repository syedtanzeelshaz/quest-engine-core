from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    TIMESTAMP,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.core.primitives.enums import Experience
from app.model.base import AuditMetadataMixin


class AppUserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AppUserAud(Base):
    """Audit table for identity.app_user."""
    __tablename__ = "app_user_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(AppUserAud)
class AppUser(Base, AuditMetadataMixin):
    """Pure security and authentication principal entity."""
    __tablename__ = "app_user"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    experience: Mapped[Experience | None] = mapped_column(
        SQLEnum(Experience, native_enum=False, length=50),
        nullable=True,
        default=Experience.CUSTOMER,
    )
    status: Mapped[AppUserStatus | None] = mapped_column(
        SQLEnum(AppUserStatus, native_enum=False, length=50),
        nullable=True,
        default=AppUserStatus.ACTIVE,
    )
