import pytest
from app.models.models import Users, Merch, Inventory
from app.services.services import InventoryService,UserService,TransactionService
from sqlalchemy.future import select
from tests.conftest import db




@pytest.mark.asyncio
async def test_buy_item(db):
    user = Users(id=1, username="amir", coins=100, password_hash = "asdasd")
    item = Merch(id=1, name="cap",price=10)

    db.add(user)
    db.add(item)
    await db.commit()

    service = InventoryService(db)

    await service.buy_item("cap", 1)

    inventory = await db.scalar(
        select(Inventory).where(Inventory.user_id == 1)
    )

    assert inventory is not None
    assert inventory.quantity == 1


@pytest.mark.asyncio
async def test_get_user(db):
    user = Users(id=1, username="amir", coins=100, password_hash = "asdasd")
    item = Merch(id=1, name="cap",price=10)

    db.add(user)
    db.add(item)
    await db.commit()

    service_inv = InventoryService(db)

    await service_inv.buy_item("cap", 1)

    service_user = UserService(db)

    result = await service_user.get_user(1)

    assert result["coins"] == 90
    assert result["inventory"] == [{"type":"cap","quantity":1}]
    assert result["coinHistory"]["sent"] == []
    assert result["coinHistory"]["received"] == []



@pytest.mark.asyncio
async def test_send_coin_success(db):
    sender = Users(id=1, username="a", coins=200, password_hash="x")
    receiver = Users(id=2, username="b", coins=50, password_hash="x")

    db.add_all([sender, receiver])
    await db.commit()

    service = TransactionService(db)

    await service.send_coin(1, "b", 100)

    updated_sender = await db.get(Users, 1)
    updated_receiver = await db.get(Users, 2)

    assert updated_sender.coins == 100
    assert updated_receiver.coins == 150

