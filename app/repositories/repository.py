from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Users
from app.models.models import Inventory
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






class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.inventory_repo = InventoryRepository(db)

    async def buy_item(self, item_name: str, user_id: int):
        user = await self.user_repo.get_info(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        item = await self.inventory_repo.get_merch_by_name(item_name)
        if not item:
            raise ItemNotFoundError("Товар не найден")

        inventory_item = await self.inventory_repo.get_user_item(
            user_id=user_id,
            merch_id=item.id
        )

        if inventory_item:
            inventory_item.quantity += 1
        else:
            await self.inventory_repo.create_purchase(
                user_id=user_id,
                merch_id=item.id
            )

        await self.db.commit()

    async def get_inventory(self, user_id:int):
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
