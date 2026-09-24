from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest

from app.core.database import AsyncSessionLocal
import app.main


def test_app_imports_cleanly():
    """Smoke test ensuring all modules, route schemas, and dependencies load cleanly."""
    assert app.main.app is not None


@pytest.mark.anyio
async def test_database_session_factory_wireup():
    """
    Smoke test ensuring the async database session factory and driver stack initialize cleanly.

    Does not execute any queries or require network access to PostgreSQL, but exercises
    the real AsyncSessionLocal context lifecycle and async driver dependencies (e.g. greenlet).
    """
    async with AsyncSessionLocal() as session:
        assert session is not None


def test_app_lifespan_boots_cleanly():
    """
    Smoke test ensuring FastAPI's ASGI lifespan, middleware, and health endpoints boot cleanly.

    Mocks the network database ping and migration execution so the test remains 100% offline,
    while verifying that app configuration, lifespan context, and routing work end-to-end.
    """
    with patch("app.core.bootstrap.check_database_connection", new_callable=AsyncMock), \
         patch("app.core.bootstrap.run_database_migrations"):
        with TestClient(app.main.app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
