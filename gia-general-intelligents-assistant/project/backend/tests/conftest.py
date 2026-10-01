import os
import sys
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["GIA_DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp.name}"
os.environ.pop("GIA_USE_REAL_LLM", None)
os.environ.pop("GIA_ALLOW_NETWORK", None)
os.environ.pop("GIA_ALLOW_CODE_EXEC", None)


@pytest_asyncio.fixture
async def client():
    # Import after env is set
    from app.main import app
    from app.models.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
