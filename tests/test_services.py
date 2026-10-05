from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.repositories.repository import UserRepository
from app.models.models import Users

import pytest

from app.services.services import UserService, InventoryService, TransactionService, MerchService
from app.services.services_errors import UserNotFoundError, ItemNotFoundError,SelfTransferError
from app.cache.cache import RedisCache

@pytest.fixture
def mock_db() -> AsyncMock:
    """
    Mock AsyncSession
    """
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


class TestUserService:
    @pytest.mark.asyncio
    async def test_get_user_success(self):
        service = UserService(db=None)


        service.user_repo.get_by_id = AsyncMock(return_value=type("User", (), {"coins": 500}))
        service.inventory_repo.get_inventory = AsyncMock(return_value=[])
        service.transaction_repo.get_history_from_user = AsyncMock(return_value=[])
        service.transaction_repo.get_history_to_user = AsyncMock(return_value=[])

        result = await service.get_user(1)

        assert result["coins"] == 500
        assert result["inventory"] == []
        assert result["coinHistory"]["sent"] == []
        assert result["coinHistory"]["received"] == []
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        service = UserService(db=None)

        service.user_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(UserNotFoundError):
            await service.get_user(1)

class TestMerchService:
    @pytest.mark.asyncio
    async def test_get_merch_success(self):
        fake_cache = RedisCache(redis_url="redis://fake:6379/0")
        service = MerchService(db=None, cache = fake_cache)
    
        service.cache = AsyncMock()
        service.cache.get.return_value = None

        fake_item = type("Merch", (), {"id": 1, "name": "cup", "price": 10})()
        service.merch_repo.get_merch_by_name = AsyncMock(return_value=fake_item)

        result = await service.get_merch_by_name("cup")

        service.cache.set.assert_called_once()

class TestInventoryService:
    @pytest.mark.asyncio
    async def test_buy_item_increase_quantity(self):
        db = AsyncMock()
        service = InventoryService(db)

        fake_user = type("User", (), {"id": 1,"coins":100})()
        fake_item = type("Merch", (), {"id": 1,"name":"cap","price":10})()
        fake_inventory = type("Inventory", (), {"quantity": 2})()

        service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        service.merch_repo.get_merch_by_name = AsyncMock(return_value=fake_item)
        service.inventory_repo.get_user_item_for_update= AsyncMock(return_value=fake_inventory)
        service.inventory_repo.create_purchase = AsyncMock()
        service.purchase_history_repo.create_purchase = AsyncMock()
        db.begin = MagicMock(return_value=AsyncMock())
        
        await service.buy_item("cap", 1)

        assert fake_inventory.quantity == 3
        service.inventory_repo.create_purchase.assert_not_called()
 
    @pytest.mark.asyncio
    async def test_buy_item_create_new(self):
        db = AsyncMock()
        service = InventoryService(db)
        
        fake_user = type("User", (), {"id": 1,"coins":100})()
        fake_item = type("Merch", (), {"id": 10,"name":"cap","price":10})()

        fake_inventory = type("Inventory", (), {"quantity": 2})()

        service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        service.merch_repo.get_merch_by_name = AsyncMock(return_value=fake_item)
        service.inventory_repo.get_user_item_for_update = AsyncMock(return_value=None)
        service.inventory_repo.create_purchase = AsyncMock()
        service.purchase_history_repo.create_purchase = AsyncMock()
        db.begin = MagicMock(return_value=AsyncMock())
        await service.buy_item("cap", 1)

        service.inventory_repo.create_purchase.assert_awaited_once_with(
            user_id=1,
            merch_id=10
        )

    @pytest.mark.asyncio
    async def test_buy_item_user_not_found(self):
        db = AsyncMock()
        service = InventoryService(db)
        service.user_repo.get_by_id_for_update = AsyncMock(return_value=None)

        db.begin = MagicMock(return_value=AsyncMock())
        with pytest.raises(UserNotFoundError):
            await service.buy_item("cap", 1)

    @pytest.mark.asyncio
    async def test_buy_item_item_not_found(self):
        db = AsyncMock()
        service = InventoryService(db)
        fake_user = type("User", (), {"id": 1})()
        service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)

        service.merch_repo.get_merch_by_name = AsyncMock(return_value=None)

        db.begin = MagicMock(return_value=AsyncMock())
        with pytest.raises(ItemNotFoundError):
            await service.buy_item("cap", 1)



class TestTransactionService:
    @pytest.mark.asyncio
    async def test_send_coin(self):
        db = AsyncMock()
        service = TransactionService(db)

        fake_sender = type("User",(),{"id":1,"coins":200})()
        fake_receiver = type("User",(),{"id":2, "username":"Amir","coins":0})()

        service.user_repo.get_by_id_for_update = AsyncMock(return_value = fake_sender)
        service.user_repo.get_by_username_for_update = AsyncMock(return_value = fake_receiver) 
        service.transaction_repo.create = AsyncMock()

        db.begin = MagicMock(return_value=AsyncMock())

        await service.send_coin(1,"Amirka",100)
        assert fake_receiver.coins == 100
        assert fake_sender.coins == 100

        service.user_repo.get_by_id_for_update.assert_called_once_with(1)
        service.user_repo.get_by_username_for_update.assert_called_once_with("Amirka")

        service.transaction_repo.create.assert_called_once()
        

    @pytest.mark.asyncio
    async def test_send_coin_sender_not_found(self):
        db = AsyncMock()
        service = TransactionService(db)

        fake_receiver = type("User",(),{"id":2, "username":"Amir","coins":0})()
        service.user_repo.get_by_id_for_update = AsyncMock(return_value = None)
        service.user_repo.get_by_username_for_update = AsyncMock(return_value = fake_receiver) 
        db.begin = MagicMock(return_value=AsyncMock())

        with pytest.raises(UserNotFoundError):
            await service.send_coin(1,"Amirka",100)


        service.user_repo.get_by_id_for_update.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_send_coin_sender_eq_receiver(self):
        db = AsyncMock()
        service = TransactionService(db)

        fake_user = type("User",(),{"id":1, "username":"Amir","coins":500})()

        service.user_repo.get_by_id_for_update = AsyncMock(return_value = fake_user)
        service.user_repo.get_by_username_for_update = AsyncMock(return_value = fake_user)
        db.begin = MagicMock(return_value=AsyncMock())


        with pytest.raises(SelfTransferError):
            await service.send_coin(1,"Amirka",100)

