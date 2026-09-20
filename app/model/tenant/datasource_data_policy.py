from typing import Any
from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, PrimaryKeyConstraint, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import TimestampMixin


class DatasourceDataPolicyAud(Base, TimestampMixin):
    """Audit table for tenant.datasource_data_policy."""
    __tablename__ = "datasource_data_policy_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    datasource_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    policy_definition: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


@audited(DatasourceDataPolicyAud)
class DatasourceDataPolicy(Base, TimestampMixin):
    """Policy governing field and table level data access restrictions on a datasource."""
    __tablename__ = "datasource_data_policy"
    __table_args__ = {"schema": "tenant"}

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
    datasource_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenant.datasource.id", ondelete="CASCADE"),
        nullable=False,
    )
    policy_definition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )

    # Relationships
    datasource: Mapped["Datasource"] = relationship("Datasource", foreign_keys=[datasource_id])  # type: ignore[name-defined]
