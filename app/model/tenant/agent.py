from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class AgentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    INACTIVE = "INACTIVE"


class AgentAud(Base):
    """Audit table for tenant.agent."""
    __tablename__ = "agent_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    system_instructions: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(AgentAud)
class Agent(Base, AuditMetadataMixin):
    """AI Agent entity created by an organization."""
    __tablename__ = "agent"
    __table_args__ = (
        UniqueConstraint("id", "org_id", name="pk_agent_id_org"),
        {"schema": "tenant"},
    )

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    system_instructions: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[AgentStatus | None] = mapped_column(
        SQLEnum(AgentStatus, native_enum=False, length=50),
        nullable=True,
    )
