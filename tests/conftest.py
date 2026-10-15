import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.models import Model
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.core.config import Settings
from app.main import app
from app.db.database import get_db
from app.services.services import UserService, InventoryService, TransactionService, MerchService
from app.cache.cache import RedisCache

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


@pytest_asyncio.fixture
async def client():
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()

# Фикстура для имитации базы данных (AsyncSession / условный db)
@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.begin = MagicMock(return_value=AsyncMock())
    return db

# Фабрика для создания фейковых пользователей
@pytest.fixture
def make_user():
    def _maker(user_id=1, username="Amir", coins=500):
        return type("User", (), {"id": user_id, "username": username, "coins": coins})()
    return _maker

# Фабрика для создания мерча
@pytest.fixture
def make_merch():
    def _maker(merch_id=1, name="cup", price=10):
        return type("Merch", (), {"id": merch_id, "name": name, "price": price})()
    return _maker

# Фабрика для инвентаря
@pytest.fixture
def make_inventory():
    def _maker(quantity=2):
        return type("Inventory", (), {"quantity": quantity})()
    return _maker

# --- Фикстуры сервисов ---

@pytest.fixture
def user_service(mock_db):
    service = UserService(db=mock_db)
    service.user_repo = AsyncMock()
    service.inventory_repo = AsyncMock()
    service.transaction_repo = AsyncMock()
    return service

@pytest.fixture
def merch_service(mock_db):
    fake_cache = RedisCache(redis_url="redis://fake:6379/0")
    service = MerchService(db=mock_db, cache=fake_cache)
    service.cache = AsyncMock()
    service.merch_repo = AsyncMock()
    return service

@pytest.fixture
def inventory_service(mock_db):
    service = InventoryService(db=mock_db)
    service.user_repo = AsyncMock()
    service.merch_service = AsyncMock()
    service.inventory_repo = AsyncMock()
    service.purchase_history_repo = AsyncMock()
    return service

@pytest.fixture
def transaction_service(mock_db):
    service = TransactionService(db=mock_db)
    service.user_repo = AsyncMock()
    service.transaction_repo = AsyncMock()
    return service


async def get_test_token(client, username: str) -> str:
    response = await client.post(
        "/api/login",
        data={
            "username": username,
            "password": "test_hash",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]
