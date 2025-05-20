import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
import pytest_asyncio

# Adjust the import path to your FastAPI app instance
# This assumes your main FastAPI app instance is named 'app' in 'backend.main'
from backend.main import app 

@pytest_asyncio.fixture
async def test_client() -> AsyncClient:
    """Create an HTTP client for testing the FastAPI app, handling lifespan events."""
    async with LifespanManager(app) as manager:
        # Create a transport for the managed app
        transport = ASGITransport(app=manager.app) 
        async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
            # The base_url here is for how the client constructs requests;
            # when app=app is used, it routes internally without actual HTTP calls for that part.
            # However, if your app makes calls to itself or needs to resolve full URLs,
            # ensuring consistency is good.
            yield client 