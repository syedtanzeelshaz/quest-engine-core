from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import TimestampMixin


class OrganizationMemberAud(Base, TimestampMixin):
    """Audit table for identity.organization_member."""
    __tablename__ = "organization_member_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)


@audited(OrganizationMemberAud)
class OrganizationMember(Base, TimestampMixin):
    """Organization membership and role assignment entity."""
    __tablename__ = "organization_member"
    __table_args__ = (
        ExcludeConstraint(
            ("user_id", "="),
            ("org_id", "<>"),
            name="organization_member_one_org_per_user",
            using="gist",
        ),
        {"schema": "identity"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    org_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("identity.role.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    user = relationship("AppUser", lazy="joined")
    organization = relationship("Organization", lazy="joined")
    role = relationship("Role", lazy="joined")
