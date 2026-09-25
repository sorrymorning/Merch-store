from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.models import Model
import pytest_asyncio

from app.core.config import Settings

test_settings = Settings(
    _env_file=".env.test"
)


test_engine = create_async_engine(test_settings.DATABASE_URL)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)