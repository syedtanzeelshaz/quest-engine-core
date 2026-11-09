from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
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


class RoleAud(Base):
    """Audit table for identity.role."""
    __tablename__ = "role_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(RoleAud)
class Role(Base, AuditMetadataMixin):
    """Unified role entity across customer and operations contexts."""
    __tablename__ = "role"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    experience: Mapped[Experience | None] = mapped_column(
        SQLEnum(Experience, native_enum=False, length=50),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
