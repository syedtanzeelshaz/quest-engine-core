from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TenantRevInfo(Base):
    """Tenant audit revision metadata table."""
    __tablename__ = "revinfo"
    __table_args__ = {"schema": "tenant"}

    rev: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    revtstmp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
