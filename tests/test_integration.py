import asyncio
import pytest
from app.models.models import Users, Merch, Inventory,Transactions
from app.services.services import InventoryService,UserService,TransactionService
from sqlalchemy.future import select
from tests.conftest import db, client,get_test_token

# TODO: Реализовать тесты на Pg


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

    response = await client.get(
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
        "/api/send_coin",
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

@pytest.mark.asyncio
async def test_concurrent_buy_merch(client, db):
    users = [
        Users(username="buyer1", password_hash="test_hash", coins=1000),
        Users(username="buyer2", password_hash="test_hash", coins=1000),
    ]
    merch = Merch(name="T-Shirt", price=200)

    db.add_all([*users, merch])
    await db.commit()

    user_ids = [user.id for user in users]

    token1 = await get_test_token(client, "buyer1")
    token2 = await get_test_token(client, "buyer2")

    responses = await asyncio.gather(
        client.get(
            "/api/buy/T-Shirt",
            headers={"Authorization": f"Bearer {token1}"},
        ),
        client.get(
            "/api/buy/T-Shirt",
            headers={"Authorization": f"Bearer {token2}"},
        ),
    )

    assert all(response.status_code == 200 for response in responses)

    for user_id in user_ids:
        user = await db.get(Users, user_id)
        await db.refresh(user)
        assert user.coins == 800

        inventory = await db.scalar(
            select(Inventory).where(
                Inventory.user_id == user_id,
                Inventory.merch_id == merch.id,
            )
        )

        assert inventory is not None
        assert inventory.quantity == 1

'''
@pytest.mark.asyncio
async def test_concurrent_transfers(client, db):
    users = [
        Users(username="sender", password_hash="test_hash", coins=1000),
        Users(username="receiver1", password_hash="test_hash", coins=0),
        Users(username="receiver2", password_hash="test_hash", coins=0),
    ]

    db.add_all(users)
    await db.commit()

    sender_id, receiver1_id, receiver2_id = [user.id for user in users]

    token = await get_test_token(client, "sender")

    responses = await asyncio.gather(
        client.post(
            "/api/send_coin",
            json={"toUser": "receiver1", "amount": 700},
            headers={"Authorization": f"Bearer {token}"},
        ),
        client.post(
            "/api/send_coin",
            json={"toUser": "receiver2", "amount": 700},
            headers={"Authorization": f"Bearer {token}"},
        ),
    )

    assert sum(response.status_code == 200 for response in responses) == 1

    await db.refresh(users[0])
    await db.refresh(users[1])
    await db.refresh(users[2])

    assert users[0].coins == 300
    assert users[1].coins + users[2].coins == 700'''
