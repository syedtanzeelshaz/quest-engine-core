from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Identity, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.model.base import AuditMetadataMixin


class RefreshToken(Base, AuditMetadataMixin):
    """Persisted refresh token record for server-side revocation support."""

    __tablename__ = "refresh_token"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
