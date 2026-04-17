from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Users
from app.models.models import Purchases
from app.models.models import Merch
from app.models.models import Transactions




class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int):
        return await self.db.get(Users, user_id)
    
    async def get_by_username(self, username: str):
        result = await self.db.execute(
            select(Users).where(Users.username == username)
        )
        return result.scalar_one_or_none()

    async def update(self, user: Users):
        self.db.add(user)






class PurchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_merch_by_name(self, name: str):
        return await self.db.scalar(
            select(Merch).where(Merch.name == name)
        )
    async def create_purchase(self, user_id: int, merch_id: int):
        purchase = Purchases(user_id=user_id, merch_id=merch_id)
        self.db.add(purchase)
    

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
