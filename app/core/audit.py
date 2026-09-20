import time
from collections import defaultdict
from collections.abc import Callable
from enum import IntEnum
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


def _get_revinfo_model(schema: str) -> type:
    """Dynamically resolve the RevInfo model corresponding to the schema."""
    if schema == "identity":
        from app.model.identity.revinfo import IdentityRevInfo
        return IdentityRevInfo
    elif schema == "tenant":
        from app.model.tenant.revinfo import TenantRevInfo
        return TenantRevInfo
    else:
        raise ValueError(f"Unsupported schema for audit revision: {schema}")


def audit_before_flush(session: Session, flush_context: Any, instances: Any) -> None:
    """
    Pre-flush listener that inspects modified, added, and deleted entities
    and schedules audit record creation.
    """
    if session.info.get("_in_audit_flush", False):
        return

    pending: list[tuple[Any, RevType, dict[str, Any] | None]] = []

    # 1. New instances (ADD)
    for obj in session.new:
        if type(obj) in AUDIT_REGISTRY:
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
    if session.info.get("_in_audit_flush", False):
        return

    pending: list[tuple[Any, RevType, dict[str, Any] | None]] | None = session.info.pop(
        "audit_pending", None
    )
    if not pending:
        return

    session.info["_in_audit_flush"] = True
    try:
        # Group pending changes by target database schema
        records_by_schema: dict[str, list[tuple[Any, RevType, dict[str, Any] | None]]] = defaultdict(list)
        for obj, revtype, snapshot in pending:
            schema_name = getattr(obj.__table__, "schema", None) or "public"
            records_by_schema[schema_name].append((obj, revtype, snapshot))

        current_timestamp_ms = int(time.time() * 1000)

        for schema_name, items in records_by_schema.items():
            revinfo_cls = _get_revinfo_model(schema_name)
            revinfo_record = revinfo_cls(revtstmp=current_timestamp_ms)
            session.add(revinfo_record)
            # Flush revinfo record to obtain generated primary key 'rev'
            session.flush([revinfo_record])
            rev_id = revinfo_record.rev

            for obj, revtype, snapshot in items:
                aud_cls = AUDIT_REGISTRY[type(obj)]
                aud_instance = aud_cls()
                aud_instance.rev = rev_id
                aud_instance.revtype = int(revtype)

                if revtype == RevType.DEL and snapshot is not None:
                    for key, value in snapshot.items():
                        if hasattr(aud_instance, key):
                            setattr(aud_instance, key, value)
                else:
                    state = inspect(obj)
                    for attr in state.mapper.column_attrs:
                        if hasattr(aud_instance, attr.key):
                            setattr(aud_instance, attr.key, getattr(obj, attr.key))

                session.add(aud_instance)

        # Flush audit records within the same transaction
        session.flush()
    finally:
        session.info["_in_audit_flush"] = False


def register_audit_listeners() -> None:
    """Register audit event listeners on the global SQLAlchemy Session class."""
    if not event.contains(Session, "before_flush", audit_before_flush):
        event.listen(Session, "before_flush", audit_before_flush)
    if not event.contains(Session, "after_flush", audit_after_flush):
        event.listen(Session, "after_flush", audit_after_flush)
