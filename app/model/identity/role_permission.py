from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    PrimaryKeyConstraint,
    SmallInteger,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class RolePermissionAud(Base):
    """Audit table for identity.role_permission."""
    __tablename__ = "role_permission_aud"
    __table_args__ = (
        PrimaryKeyConstraint("role_id", "permission_id", "rev"),
        {"schema": "identity"},
    )

    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    permission_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(RolePermissionAud)
class RolePermission(Base, AuditMetadataMixin):
    """Junction entity mapping roles to fine-grained permissions."""
    __tablename__ = "role_permission"
    __table_args__ = (
        PrimaryKeyConstraint("role_id", "permission_id"),
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        {"schema": "identity"},
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
