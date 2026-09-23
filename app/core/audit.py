import time
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session


class RevType(IntEnum):
    """Envers-compatible revision type enumeration."""
    ADD = 0
    MOD = 1
    DEL = 2


# Maps Base entity class -> Audited entity class
AUDIT_REGISTRY: dict[type, type] = {}

# Maps schema name -> RevInfo class
REVINFO_REGISTRY: dict[str, type] = {}


def audited(aud_model_cls: type) -> Callable[[type], type]:
    """
    Class decorator to mark an entity for automatic Envers-style revision auditing.

    Example:
        @audited(AppUserAud)
        class AppUser(Base):
            ...
    """
    def decorator(cls: type) -> type:
        AUDIT_REGISTRY[cls] = aud_model_cls
        return cls

    return decorator


def register_revinfo(schema: str) -> Callable[[type], type]:
    """
    Class decorator to register a RevInfo model for a given schema name.

    Example:
        @register_revinfo("identity")
        class IdentityRevInfo(Base):
            ...
    """
    def decorator(cls: type) -> type:
        REVINFO_REGISTRY[schema] = cls
        return cls

    return decorator


def _get_revinfo_model(schema: str) -> type:
    """Resolve the RevInfo model for the given schema from the registry."""
    try:
        return REVINFO_REGISTRY[schema]
    except KeyError:
        raise ValueError(f"Unsupported schema for audit revision: '{schema}'. "
                         f"Did you forget to decorate the RevInfo class with @register_revinfo?")


def audit_before_flush(session: Session, flush_context: Any, instances: Any) -> None:
    """
    Pre-flush listener that inspects modified, added, and deleted entities
    and schedules audit record creation.
    """
    if session.info.get("_in_audit_flush", False):
        return

    pending: list[tuple[Any, RevType, dict[str, Any] | None]] = []

    now_utc = datetime.now(timezone.utc)

    # 1. New instances (ADD)
    for obj in session.new:
        if type(obj) in AUDIT_REGISTRY:
            if hasattr(obj, "created_at") and obj.created_at is None:
                obj.created_at = now_utc
            if hasattr(obj, "updated_at") and obj.updated_at is None:
                obj.updated_at = now_utc
            pending.append((obj, RevType.ADD, None))

    # 2. Dirty instances (MOD)
    for obj in session.dirty:
        if type(obj) in AUDIT_REGISTRY:
            state = inspect(obj)
            has_changes = False
            for attr in state.mapper.column_attrs:
                hist = state.get_history(attr.key, True)
                if hist.has_changes():
                    has_changes = True
                    break
            if has_changes:
                if hasattr(obj, "updated_at"):
                    obj.updated_at = now_utc
                pending.append((obj, RevType.MOD, None))

    # 3. Deleted instances (DEL) - snapshot values before removal
    for obj in session.deleted:
        if type(obj) in AUDIT_REGISTRY:
            state = inspect(obj)
            snapshot: dict[str, Any] = {}
            for attr in state.mapper.column_attrs:
                hist = state.get_history(attr.key, True)
                if hist.deleted:
                    snapshot[attr.key] = hist.deleted[0]
                else:
                    snapshot[attr.key] = getattr(obj, attr.key, None)
            pending.append((obj, RevType.DEL, snapshot))

    if pending:
        session.info["audit_pending"] = pending
    else:
        session.info.pop("audit_pending", None)


def audit_after_flush(session: Session, flush_context: Any) -> None:
    """
    Post-flush listener that creates RevInfo records and snapshots audit records
    after primary entity IDs have been generated.
    """
    pending: list[tuple[Any, RevType, dict[str, Any] | None]] | None = session.info.pop(
        "audit_pending", None
    )
    if not pending:
        return

    conn = session.connection()
    current_timestamp_ms = int(time.time() * 1000)

    # Group pending changes by target database schema
    records_by_schema: dict[str, list[tuple[Any, RevType, dict[str, Any] | None]]] = defaultdict(list)
    for obj, revtype, snapshot in pending:
        schema_name = getattr(obj.__table__, "schema", None) or "public"
        records_by_schema[schema_name].append((obj, revtype, snapshot))

    for schema_name, items in records_by_schema.items():
        revinfo_cls = _get_revinfo_model(schema_name)
        revinfo_table = revinfo_cls.__table__
        stmt = (
            revinfo_table.insert()
            .values(revtstmp=current_timestamp_ms)
            .returning(revinfo_table.c.rev)
        )
        rev_id = conn.scalar(stmt)

        for obj, revtype, snapshot in items:
            aud_cls = AUDIT_REGISTRY[type(obj)]
            aud_table = aud_cls.__table__
            row_data: dict[str, Any] = {
                "rev": rev_id,
                "revtype": int(revtype),
            }

            if revtype == RevType.DEL and snapshot is not None:
                for key, value in snapshot.items():
                    if key in aud_table.c:
                        row_data[key] = value.value if isinstance(value, Enum) else value
            else:
                state = inspect(obj)
                for attr in state.mapper.column_attrs:
                    if attr.key in aud_table.c:
                        val = getattr(obj, attr.key)
                        row_data[attr.key] = val.value if isinstance(val, Enum) else val

            conn.execute(aud_table.insert().values(**row_data))


def register_audit_listeners() -> None:
    """Register audit event listeners on the global SQLAlchemy Session class."""
    if not event.contains(Session, "before_flush", audit_before_flush):
        event.listen(Session, "before_flush", audit_before_flush)
    if event.contains(Session, "after_flush_postexec", audit_after_flush):
        event.remove(Session, "after_flush_postexec", audit_after_flush)
    if not event.contains(Session, "after_flush", audit_after_flush):
        event.listen(Session, "after_flush", audit_after_flush)
