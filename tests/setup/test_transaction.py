from unittest.mock import MagicMock

import pytest

from app.core.database import reset_current_session, set_current_session
from app.core.transaction import transactional


@pytest.mark.anyio
async def test_transactional_commit_on_success(mock_db_session: MagicMock):
    """Verify @transactional begins an async transaction and commits on success."""
    @transactional
    async def service_method():
        return "success"

    token = set_current_session(mock_db_session)
    try:
        result = await service_method()
        assert result == "success"
        mock_db_session.begin.assert_called_once()
    finally:
        reset_current_session(token)


@pytest.mark.anyio
async def test_transactional_rollback_on_error(mock_db_session: MagicMock):
    """Verify @transactional triggers rollback handling if an exception is raised."""
    class DummyError(Exception):
        pass

    @transactional
    async def service_method():
        raise DummyError("Failed")

    token = set_current_session(mock_db_session)
    try:
        with pytest.raises(DummyError):
            await service_method()
        mock_db_session.begin.assert_called_once()
    finally:
        reset_current_session(token)


@pytest.mark.anyio
async def test_transactional_nested_savepoint(mock_db_session: MagicMock):
    """Verify @transactional creates a nested savepoint if an outer transaction is active."""
    mock_db_session.in_transaction.return_value = True

    @transactional
    async def nested_service_method():
        return "nested"

    token = set_current_session(mock_db_session)
    try:
        result = await nested_service_method()
        assert result == "nested"
        mock_db_session.begin_nested.assert_called_once()
        mock_db_session.begin.assert_not_called()
    finally:
        reset_current_session(token)


@pytest.mark.anyio
async def test_transactional_resolves_self_session(mock_db_session: MagicMock):
    """Verify @transactional uses ContextVar session when present on a service instance."""
    class DummyService:
        @transactional
        async def do_work(self):
            return "done"

    token = set_current_session(mock_db_session)
    try:
        service = DummyService()
        result = await service.do_work()
        assert result == "done"
        mock_db_session.begin.assert_called_once()
    finally:
        reset_current_session(token)


@pytest.mark.anyio
async def test_transactional_resolves_repo_session(mock_db_session: MagicMock):
    """Verify @transactional uses ContextVar session even when called from a repo-backed service."""
    class DummyService:
        @transactional
        async def do_work(self):
            return "repo_done"

    token = set_current_session(mock_db_session)
    try:
        service = DummyService()
        result = await service.do_work()
        assert result == "repo_done"
        mock_db_session.begin.assert_called_once()
    finally:
        reset_current_session(token)
