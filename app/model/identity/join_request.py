from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import TimestampMixin


class JoinRequestAud(Base, TimestampMixin):
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
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    initiator_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


@audited(JoinRequestAud)
class JoinRequest(Base, TimestampMixin):
    """Organization join request or invitation entity."""
    __tablename__ = "join_request"
    __table_args__ = {"schema": "identity"}

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
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    initiator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", foreign_keys=[org_id])
    user = relationship("AppUser", foreign_keys=[user_id])
    initiator = relationship("AppUser", foreign_keys=[initiator_id])
    reviewer = relationship("AppUser", foreign_keys=[reviewed_by])
