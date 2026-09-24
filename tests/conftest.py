import os
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

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
    """Fixture providing a mocked SQLAlchemy Session."""
    return MagicMock(spec=Session)
