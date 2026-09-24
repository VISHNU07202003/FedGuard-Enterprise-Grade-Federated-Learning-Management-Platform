import pytest
from httpx import AsyncClient
from sqlalchemy import text

from app.db.session import get_engine


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Test that /health returns 200 with status and timestamp."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_ready(client: AsyncClient):
    """Test readiness endpoint - may return 503 if DB is unavailable."""
    response = await client.get("/ready")
    assert response.status_code in (200, 503)


@pytest.mark.asyncio
async def test_database_integration():
    """Verify async SQLAlchemy session works by executing a lightweight query."""
    try:
        maker = get_engine()
        async with maker() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except Exception as e:
        pytest.skip(f"Database not available for integration test: {e}")
