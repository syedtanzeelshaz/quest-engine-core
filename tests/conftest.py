import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings

# Set fallback environment variables for test execution
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-32bytes!")


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing isolated Settings instance with fixed test credentials."""
    return Settings(
        JWT_SECRET_KEY="test-secret-key-for-testing-only-32bytes!",
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
    )


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Fixture providing a mocked SQLAlchemy AsyncSession supporting async context managers."""
    session = MagicMock(spec=AsyncSession)
    session.in_transaction.return_value = False

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=None)
    cm.__aexit__ = AsyncMock(return_value=None)
    cm.__enter__ = MagicMock(return_value=None)
    cm.__exit__ = MagicMock(return_value=None)
    session.begin.return_value = cm
    session.begin_nested.return_value = cm

    return session

