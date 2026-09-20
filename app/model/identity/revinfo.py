from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IdentityRevInfo(Base):
    """Identity audit revision metadata table."""
    __tablename__ = "revinfo"
    __table_args__ = {"schema": "identity"}

    rev: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    revtstmp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
