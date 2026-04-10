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

    async def update(self, user: Users):
        self.db.add(user)


    

class PurchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buy_item(self, name: str, user_id: int):
        item_id = await self.db.scalar(
            select(Merch.id).where(Merch.name == name)
        )
        if not item_id:
            raise ValueError(f"Товар с именем {name} не найден")
        
        
        purch = Purchases(user_id=user_id, merch_id=item_id) 
        self.db.add(purch)
        await self.db.flush()
        await self.db.commit()
        
        return purch
    

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
