from datetime import datetime

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class OperatorRoleAud(Base):
    """Audit table for identity.operator_role."""
    __tablename__ = "operator_role_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    operator_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(OperatorRoleAud)
class OperatorRole(Base, AuditMetadataMixin):
    """Operations multi-role junction table."""
    __tablename__ = "operator_role"
    __table_args__ = (
        UniqueConstraint("operator_id", "role_id", name="uq_operator_role"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    operator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.operator.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.role.id", ondelete="CASCADE"),
        nullable=False,
    )

