from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import text


class AuditMetadataMixin:
    """Reusable mixin for audit tracking columns."""
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("now()"),
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=text("now()"),
    )
    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
