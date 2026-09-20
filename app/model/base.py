from datetime import datetime
from sqlalchemy import BigInteger, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Reusable mixin for audit tracking columns."""
    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=func.now(),
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=func.now(),
        onupdate=func.now(),
    )
    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )
