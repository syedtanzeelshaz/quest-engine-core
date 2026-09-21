from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Enum as SQLEnum,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class OrgStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    INACTIVE = "INACTIVE"


class OrganizationAud(Base):
    """Audit table for identity.organization."""
    __tablename__ = "organization_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    slug: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(OrganizationAud)
class Organization(Base, AuditMetadataMixin):
    """Tenant organization entity."""
    __tablename__ = "organization"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[OrgStatus | None] = mapped_column(
        SQLEnum(OrgStatus, native_enum=False, length=50),
        nullable=True,
    )
