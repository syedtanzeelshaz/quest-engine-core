from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.core.audit import (
    RevType,
    audit_after_flush,
    audit_before_flush,
)
from app.model.identity import AppUser


def test_revtype_enum_values():
    assert RevType.ADD == 0
    assert RevType.MOD == 1
    assert RevType.DEL == 2


def test_audit_lifecycle_flow():
    """Verify the two-phase audit event collection (before_flush and after_flush)."""
    session = MagicMock(spec=Session)
    session.info = {}

    # 1. Simulate new entity (ADD)
    user = AppUser(
        id=101,
        email="alice@example.com",
        password_hash="secret_hash",
        first_name="Alice",
    )
    session.new = [user]
    session.dirty = []
    session.deleted = []

    # Run before_flush
    audit_before_flush(session, None, None)
    assert "audit_pending" in session.info
    assert len(session.info["audit_pending"]) == 1
    obj, revtype, _ = session.info["audit_pending"][0]
    assert obj is user
    assert revtype == RevType.ADD

    # Run after_flush with connection mock returning rev=1
    conn_mock = session.connection.return_value
    conn_mock.scalar.return_value = 1

    audit_after_flush(session, None)

    # Verify revinfo inserted via scalar() and audit record inserted via execute()
    assert conn_mock.scalar.called
    assert conn_mock.execute.called
