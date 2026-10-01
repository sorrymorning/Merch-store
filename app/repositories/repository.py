from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Users
from app.models.models import Inventory
from app.models.models import Merch
from app.models.models import Transactions
from app.models.models import PurchaseHistory


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int):
        return await self.db.get(Users, user_id)
    
    async def get_by_id_for_update(self, user_id: int):
        result = await self.db.execute(
            select(Users)
            .where(Users.id == user_id)
            .with_for_update() 
        )
        return result.scalars().first()

    async def get_by_username(self, username: str):
        result = await self.db.execute(
            select(Users).where(Users.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username_for_update(self, username: str):
        result = await self.db.execute(
            select(Users)
            .where(Users.username == username)
            .with_for_update()
        )
        return result.scalars().first()
   
    async def update(self, user: Users):
        self.db.add(user)

    async def create(self, username: str, password_hash: str):
        user = Users(
            username=username,
            password_hash=password_hash,
            coins=1000
        )

        self.db.add(user)
        await self.db.flush()

        return user


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_merch_by_name(self, name: str):
        return await self.db.scalar(
            select(Merch).where(Merch.name == name)
        )

    async def get_user_item_for_update(self, user_id: int, merch_id: int):
        result = await self.db.execute(
            select(Inventory)
            .where(
                Inventory.user_id == user_id,
                Inventory.merch_id == merch_id
            )
            .with_for_update()
        )
        return result.scalars().first()
 
    async def create_purchase(self, user_id: int, merch_id: int):
        purchase = Inventory(
            user_id=user_id,
            merch_id=merch_id,
            quantity=1
        )
        self.db.add(purchase)
    
    async def get_inventory(self, user_id: int):
        result = await self.db.execute(
            select(
                Merch.name.label("type"),
                Inventory.quantity.label("quantity")
            )
            .join(Merch, Inventory.merch_id == Merch.id)
            .where(Inventory.user_id == user_id)
        )
        return result.all()
    

class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, from_user_id: int, to_user_id: int, amount: int):
        transaction = Transactions(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            amount=amount
        )
        self.db.add(transaction)
        return transaction
    
    async def get_history_from_user(self,user_id):
        result = await self.db.execute(
            select(
                Users.username.label("toUser"),
                Transactions.amount.label("amount")
            )
            .join(Users,Transactions.to_user_id == Users.id)
            .where(Transactions.from_user_id == user_id)
        )

        return result.all()


    async def get_history_to_user(self,user_id):
        result = await self.db.execute(
            select(
                Users.username.label("fromUser"),
                Transactions.amount.label("amount")
            )
            .join(Users,Transactions.from_user_id == Users.id)
            .where(Transactions.to_user_id == user_id)
        )
        return result.all()

class PurchaseHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_purchase(
        self,
        user_id: int,
        merch_id: int,
        quantity: int = 1
    ):
        purchase = PurchaseHistory(
            user_id=user_id,
            merch_id=merch_id,
            quantity=quantity
        )

        self.db.add(purchase)
        await self.db.flush()

        return purchase
