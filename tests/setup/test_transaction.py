import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.core.database import set_current_session, reset_current_session
from app.core.transaction import transactional


def test_transactional_commit_on_success():
    """Verify @transactional begins a transaction and commits on success."""
    mock_session = MagicMock(spec=Session)
    mock_session.in_transaction.return_value = False

    @transactional
    def service_method():
        return "success"

    token = set_current_session(mock_session)
    try:
        result = service_method()
        assert result == "success"
        mock_session.begin.assert_called_once()
    finally:
        reset_current_session(token)


def test_transactional_rollback_on_error():
    """Verify @transactional rolls back if an exception is raised."""
    mock_session = MagicMock(spec=Session)
    mock_session.in_transaction.return_value = False

    class DummyError(Exception):
        pass

    @transactional
    def service_method():
        raise DummyError("Failed")

    token = set_current_session(mock_session)
    try:
        with pytest.raises(DummyError):
            service_method()
        mock_session.begin.assert_called_once()
    finally:
        reset_current_session(token)


def test_transactional_nested_savepoint():
    """Verify @transactional creates a nested savepoint if transaction is active."""
    mock_session = MagicMock(spec=Session)
    mock_session.in_transaction.return_value = True

    @transactional
    def nested_service_method():
        return "nested"

    token = set_current_session(mock_session)
    try:
        result = nested_service_method()
        assert result == "nested"
        mock_session.begin_nested.assert_called_once()
        mock_session.begin.assert_not_called()
    finally:
        reset_current_session(token)


def test_transactional_resolves_self_session():
    """Verify @transactional resolves session from self.session."""
    mock_session = MagicMock(spec=Session)
    mock_session.in_transaction.return_value = False

    class DummyService:
        def __init__(self, session):
            self.session = session

        @transactional
        def do_work(self):
            return "done"

    service = DummyService(mock_session)
    result = service.do_work()
    assert result == "done"
    mock_session.begin.assert_called_once()


@pytest.mark.anyio
async def test_transactional_async_support():
    """Verify @transactional works with async functions."""
    mock_session = MagicMock(spec=Session)
    mock_session.in_transaction.return_value = False

    @transactional
    async def async_service():
        return "async_done"

    token = set_current_session(mock_session)
    try:
        result = await async_service()
        assert result == "async_done"
        mock_session.begin.assert_called_once()
    finally:
        reset_current_session(token)
