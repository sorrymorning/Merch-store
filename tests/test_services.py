from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from app.repositories.repository import UserRepository
from app.models.models import Users

import pytest

from app.services.services import UserService, InventoryService, TransactionService, MerchService
from app.services.services_errors import UserNotFoundError, ItemNotFoundError,SelfTransferError





class TestUserService:
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service):
        user_service.user_repo.get_by_id = AsyncMock(return_value=type("User", (), {"coins": 500}))
        user_service.inventory_repo.get_inventory = AsyncMock(return_value=[])
        user_service.transaction_repo.get_history_from_user = AsyncMock(return_value=[])
        user_service.transaction_repo.get_history_to_user = AsyncMock(return_value=[])

        result = await user_service.get_user(1)

        assert result["coins"] == 500
        assert result["inventory"] == []
        assert result["coinHistory"]["sent"] == []
        assert result["coinHistory"]["received"] == []
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        user_service.user_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(UserNotFoundError):
            await user_service.get_user(1)


class TestMerchService:
    @pytest.mark.asyncio
    async def test_get_merch_success(self, merch_service, make_merch):
        merch_service.cache.get.return_value = None

        fake_item = make_merch(merch_id=1, name="cup", price=10)
        merch_service.merch_repo.get_merch_by_name = AsyncMock(return_value=fake_item)

        await merch_service.get_merch_by_name("cup")

        merch_service.cache.set.assert_called_once()


class TestInventoryService:
    @pytest.mark.asyncio
    async def test_buy_item_increase_quantity(self, inventory_service, make_user, make_merch, make_inventory):
        fake_user = make_user(user_id=1, coins=100)
        fake_item = make_merch(merch_id=1, name="cap", price=10)
        fake_inventory = make_inventory(quantity=2)

        inventory_service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        inventory_service.merch_service.get_merch_by_name = AsyncMock(return_value=fake_item)
        inventory_service.inventory_repo.get_user_item_for_update = AsyncMock(return_value=fake_inventory)

        await inventory_service.buy_item("cap", 1)

        assert fake_inventory.quantity == 3
        inventory_service.inventory_repo.create_purchase.assert_not_called()
 
    @pytest.mark.asyncio
    async def test_buy_item_create_new(self, inventory_service, make_user, make_merch):
        fake_user = make_user(user_id=1, coins=100)
        fake_item = make_merch(merch_id=10, name="cap", price=10)

        inventory_service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        inventory_service.merch_service.get_merch_by_name = AsyncMock(return_value=fake_item)
        inventory_service.inventory_repo.get_user_item_for_update = AsyncMock(return_value=None)

        await inventory_service.buy_item("cap", 1)

        inventory_service.inventory_repo.create_purchase.assert_awaited_once_with(
            user_id=1,
            merch_id=10
        )

    @pytest.mark.asyncio
    async def test_buy_item_user_not_found(self, inventory_service):
        inventory_service.user_repo.get_by_id_for_update = AsyncMock(return_value=None)

        with pytest.raises(UserNotFoundError):
            await inventory_service.buy_item("cap", 1)

    @pytest.mark.asyncio
    async def test_buy_item_item_not_found(self, inventory_service, make_user):
        fake_user = make_user(user_id=1)
        inventory_service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        inventory_service.merch_service.get_merch_by_name = AsyncMock(return_value=None)

        with pytest.raises(ItemNotFoundError):
            await inventory_service.buy_item("cap", 1)


class TestTransactionService:
    @pytest.mark.asyncio
    async def test_send_coin(self, transaction_service, make_user):
        fake_sender = make_user(user_id=1, coins=200)
        fake_receiver = make_user(user_id=2, username="Amir", coins=0)

        transaction_service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_sender)
        transaction_service.user_repo.get_by_username_for_update = AsyncMock(return_value=fake_receiver)

        await transaction_service.send_coin(1, "Amirka", 100)
        
        assert fake_receiver.coins == 100
        assert fake_sender.coins == 100

        transaction_service.user_repo.get_by_id_for_update.assert_called_once_with(1)
        transaction_service.user_repo.get_by_username_for_update.assert_called_once_with("Amirka")
        transaction_service.transaction_repo.create.assert_called_once()
        

    @pytest.mark.asyncio
    async def test_send_coin_sender_not_found(self, transaction_service, make_user):
        fake_receiver = make_user(user_id=2, username="Amir", coins=0)
        transaction_service.user_repo.get_by_id_for_update = AsyncMock(return_value=None)
        transaction_service.user_repo.get_by_username_for_update = AsyncMock(return_value=fake_receiver)

        with pytest.raises(UserNotFoundError):
            await transaction_service.send_coin(1, "Amirka", 100)

        transaction_service.user_repo.get_by_id_for_update.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_send_coin_sender_eq_receiver(self, transaction_service, make_user):
        fake_user = make_user(user_id=1, username="Amir", coins=500)

        transaction_service.user_repo.get_by_id_for_update = AsyncMock(return_value=fake_user)
        transaction_service.user_repo.get_by_username_for_update = AsyncMock(return_value=fake_user)

        with pytest.raises(SelfTransferError):
            await transaction_service.send_coin(1, "Amirka", 100)
