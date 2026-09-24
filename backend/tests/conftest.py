"""Test fixtures for FedGuard backend tests."""

import os
import pytest
import pytest_asyncio
from pathlib import Path
from httpx import ASGITransport, AsyncClient


def _load_backend_env():
    """Load backend/.env into os.environ so secrets are available in tests."""
    env_path = Path(__file__).parents[1] / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    # Only set if not already overridden by the real environment (e.g. CI)
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()


# Load env BEFORE importing app so pydantic-settings / get_secret picks it up.
_load_backend_env()

from app.main import app  # noqa: E402


@pytest_asyncio.fixture
async def client():
    """Create an async test client for the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
