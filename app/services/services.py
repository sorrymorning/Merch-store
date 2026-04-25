from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repository import UserRepository
from app.repositories.repository import InventoryRepository
from app.repositories.repository import TransactionRepository
from services_errors import (UserNotFoundError, 
                             NotEnoughCoinsError, 
                             SelfTransferError,
                             ItemNotFoundError
                                )





class UserService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.inventory_repo = InventoryRepository(db)

    async def get_user(self, user_id:int):
        user = await self.user_repo.get_by_id(user_id)
        inventory = await self.inventory_repo.get_inventory(user_id)
        transaction = ...


class TransactionService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    async def send_coin(self, from_user_id: int, to_username: str, amount: int):
        sender = await self.user_repo.get_by_id(from_user_id)
        receiver = await self.user_repo.get_by_username(to_username)

        if not sender:
            raise UserNotFoundError("Отправитель не найден")

        if not receiver:
            raise UserNotFoundError("Получатель не найден")

        if sender.coins < amount:
            raise NotEnoughCoinsError("Недостаточно средств")

        if sender.id == receiver.id:
            raise SelfTransferError("Нельзя отправить самому себе")

        sender.coins -= amount
        receiver.coins += amount

        await self.transaction_repo.create(
            from_user_id=sender.id,
            to_user_id=receiver.id,
            amount=amount
        )

        await self.db.commit()

# Исправить инвентарь!!!
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








class PurchService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.user_repo = PurchRepository(db)
    
    async def buy_item(self, item_name: str, user_id: int):
        
        return await self.user_repo.buy_item(item_name,user_id)
