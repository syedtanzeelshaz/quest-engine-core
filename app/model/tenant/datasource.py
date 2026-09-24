from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    ForeignKey,
    Identity,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit import audited
from app.core.database import Base
from app.model.base import AuditMetadataMixin


class DatasourceCategory(StrEnum):
    DATABASE = "DATABASE"
    DOCUMENT = "DOCUMENT"
    FILE = "FILE"


class DatasourceType(StrEnum):
    MONGODB = "MONGODB"
    MYSQL = "MYSQL"
    NOTION = "NOTION"
    PDF = "PDF"
    POSTGRESQL = "POSTGRESQL"


class DatasourceApprovalStatus(StrEnum):
    APPROVED = "APPROVED"
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class DatasourceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    INACTIVE = "INACTIVE"
    METADATA_DISCOVERY_FAILED = "METADATA_DISCOVERY_FAILED"


class DatasourceAud(Base):
    """Audit table for tenant.datasource."""
    __tablename__ = "datasource_aud"
    __table_args__ = (
        PrimaryKeyConstraint("id", "rev"),
        {"schema": "tenant"},
    )

    id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    rev: Mapped[int] = mapped_column(BigInteger, nullable=False)
    revtype: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    org_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    connection_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


@audited(DatasourceAud)
class Datasource(Base, AuditMetadataMixin):
    """Datasource entity representing an external connected customer data source."""
    __tablename__ = "datasource"
    __table_args__ = (
        UniqueConstraint("id", "org_id", name="pk_datasource_id_org"),
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
    category: Mapped[DatasourceCategory] = mapped_column(
        SQLEnum(DatasourceCategory, native_enum=False, length=50),
        nullable=False,
    )
    type: Mapped[DatasourceType] = mapped_column(
        SQLEnum(DatasourceType, native_enum=False, length=50),
        nullable=False,
    )
    connection_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    approval_status: Mapped[DatasourceApprovalStatus | None] = mapped_column(
        SQLEnum(DatasourceApprovalStatus, native_enum=False, length=50),
        nullable=True,
    )
    status: Mapped[DatasourceStatus | None] = mapped_column(
        SQLEnum(DatasourceStatus, native_enum=False, length=50),
        nullable=True,
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("identity.app_user.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


DATASOURCE_TYPES_BY_CATEGORY: dict[DatasourceCategory, set[DatasourceType]] = {
    DatasourceCategory.DATABASE: {
        DatasourceType.MONGODB,
        DatasourceType.MYSQL,
        DatasourceType.POSTGRESQL,
    },
    DatasourceCategory.DOCUMENT: {
        DatasourceType.NOTION,
    },
    DatasourceCategory.FILE: {
        DatasourceType.PDF,
    },
}
