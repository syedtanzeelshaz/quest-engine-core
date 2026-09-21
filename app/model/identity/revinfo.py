from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import register_revinfo
from app.core.database import Base


@register_revinfo("identity")
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
