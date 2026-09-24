from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKeyConstraint,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class AgentDatasourceAud(Base):
    """Audit table for tenant.agent_datasource."""
    __tablename__ = "agent_datasource_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    agent_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    datasource_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(AgentDatasourceAud)
class AgentDatasource(Base, AuditMetadataMixin):
    """Mapping between an Agent and an authorized Datasource within the same organization."""
    __tablename__ = "agent_datasource"
    __table_args__ = (
        ForeignKeyConstraint(
            ["agent_id", "org_id"],
            ["tenant.agent.id", "tenant.agent.org_id"],
            ondelete="CASCADE",
            name="fk_agent_datasource_agent",
        ),
        ForeignKeyConstraint(
            ["datasource_id", "org_id"],
            ["tenant.datasource.id", "tenant.datasource.org_id"],
            ondelete="CASCADE",
            name="fk_agent_datasource_datasource",
        ),
        UniqueConstraint("agent_id", "datasource_id", name="uq_agent_datasource"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    agent_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    org_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    datasource_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id, org_id])
    datasource = relationship("Datasource", foreign_keys=[datasource_id, org_id], overlaps="agent")
