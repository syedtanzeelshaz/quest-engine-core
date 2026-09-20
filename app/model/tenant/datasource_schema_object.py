from typing import Any
from sqlalchemy import BigInteger, ForeignKey, Identity, PrimaryKeyConstraint, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.audit import audited
from app.core.database import Base
from app.model.base import TimestampMixin


class DatasourceSchemaObjectAud(Base, TimestampMixin):
    """Audit table for tenant.datasource_schema_object."""
    __tablename__ = "datasource_schema_object_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    datasource_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    object_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    object_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


@audited(DatasourceSchemaObjectAud)
class DatasourceSchemaObject(Base, TimestampMixin):
    """Discovered schema object (table, view, collection, column) of a datasource."""
    __tablename__ = "datasource_schema_object"
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
    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    object_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    datasource: Mapped["Datasource"] = relationship("Datasource", foreign_keys=[datasource_id])  # type: ignore[name-defined]
