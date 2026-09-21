from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class AgentAccessPolicyAud(Base):
    """Audit table for tenant.agent_access_policy."""
    __tablename__ = "agent_access_policy_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    agent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    policy_definition: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(AgentAccessPolicyAud)
class AgentAccessPolicy(Base, AuditMetadataMixin):
    """Policy governing which users/roles may interact with an Agent."""
    __tablename__ = "agent_access_policy"
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
    agent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tenant.agent.id", ondelete="CASCADE"),
        nullable=False,
    )
    policy_definition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])
