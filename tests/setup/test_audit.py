from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.core.audit import (
    RevType,
    audit_after_flush,
    audit_before_flush,
)
from app.model.identity import AppUser, AppUserAud, IdentityRevInfo


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

    # Run after_flush with patched revinfo
    revinfo_mock = IdentityRevInfo(rev=1, revtstmp=1700000000000)
    revinfo_mock.rev = 1

    with patch("app.core.audit._get_revinfo_model", return_value=MagicMock(return_value=revinfo_mock)):
        audit_after_flush(session, None)

    # Session.add should have been called for revinfo and AppUserAud
    added_instances = [call.args[0] for call in session.add.call_args_list]
    aud_instances = [inst for inst in added_instances if isinstance(inst, AppUserAud)]

    assert len(aud_instances) == 1
    aud = aud_instances[0]
    assert aud.rev == 1
    assert aud.revtype == 0
    assert aud.id == 101
    assert aud.email == "alice@example.com"
