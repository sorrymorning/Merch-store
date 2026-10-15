import pytest
from app.models.models import Users, Merch, Inventory,Transactions
from app.services.services import InventoryService,UserService,TransactionService
from sqlalchemy.future import select
from tests.conftest import db, client,get_test_token




@pytest.mark.asyncio
async def test_buy_merch_success(client, db):
    user = Users(
        username="buyer",
        password_hash="test_hash",
        coins=1000,
    )
    merch = Merch(
        name="T-Shirt",
        price=200,
    )

    db.add_all([user, merch])
    await db.flush()

    user_id = user.id
    merch_id = merch.id

    await db.commit()

    token = await get_test_token(client, "buyer")

    response = await client.post(
        "/api/buy/T-Shirt",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    await db.refresh(user)
    assert user.coins == 800

    inventory = await db.scalar(
        select(Inventory).where(
            Inventory.user_id == user_id,
            Inventory.merch_id == merch_id,
        )
    )

    assert inventory is not None
    assert inventory.quantity == 1

@pytest.mark.asyncio
async def test_send_coin_success(client, db):
    user1 = Users(
        username="sender",
        password_hash="test_hash",
        coins=1000,
    )
    user2 = Users(
        username="receiver",
        password_hash="test_hash",
        coins=1000,
    )

    db.add_all([user1, user2])
    await db.flush()
    await db.commit()

    token = await get_test_token(client, "sender")

    response = await client.post(
        "/api/sendCoin",
        json = {"toUser":"receiver","amount":100},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    await db.refresh(user2)
    await db.refresh(user1)

    assert user2.coins == 1100
    assert user1.coins == 900

@pytest.mark.asyncio
async def test_get_info_success(client, db):
    user = Users(
        username="buyer",
        password_hash="test_hash",
        coins=800,
    )
    other_user = Users(
        username="seller",
        password_hash="test_hash",
        coins=1200,
    )

    db.add_all([user, other_user])
    await db.flush()

    merch = Merch(name="T-Shirt", price=200)
    db.add(merch)
    await db.flush()

    inventory = Inventory(
        user_id=user.id,
        merch_id=merch.id,
        quantity=2,
    )
    db.add(inventory)

    received_transaction = Transactions(
        from_user_id=other_user.id,
        to_user_id=user.id,
        amount=100,
    )
    sent_transaction = Transactions(
        from_user_id=user.id,
        to_user_id=other_user.id,
        amount=50,
    )
    db.add_all([received_transaction, sent_transaction])
    await db.commit()

    token = await get_test_token(client, "buyer")

    response = await client.get(
        "/api/info",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Assert: проверяем ответ
    assert response.status_code == 200

    data = response.json()

    assert data["coins"] == 800

    assert data["inventory"] == [
        {"type": "T-Shirt", "quantity": 2}
    ]

    assert data["coinHistory"]["received"] == [
        {"fromUser": "seller", "amount": 100}
    ]
