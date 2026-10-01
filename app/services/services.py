import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repository import UserRepository
from app.repositories.repository import InventoryRepository
from app.repositories.repository import TransactionRepository, PurchaseHistoryRepository
from app.services.services_errors import (UserNotFoundError, 
                             NotEnoughCoinsError, 
                             SelfTransferError,
                             ItemNotFoundError,
                             UserAlreadyExistsError,
                             InvalidCredentialsError
                                )

    



class UserService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.inventory_repo = InventoryRepository(db)

    async def get_user(self, user_id:int):
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError("Пользователь не найден")
        inventory_rows, sent_rows, received_rows = await asyncio.gather( self.inventory_repo.get_inventory(user_id),
            self.transaction_repo.get_history_from_user(user_id),
            self.transaction_repo.get_history_to_user(user_id)
        )
        
        return {
            "coins": user.coins,
            "inventory": [
                {"type": row.type, "quantity": row.quantity} for row in inventory_rows
            ],
            "coinHistory": {
                "received": [{"fromUser": row.fromUser, "amount": row.amount} for row in received_rows],
                "sent": [{"toUser": row.toUser, "amount": row.amount} for row in sent_rows]
            }
        }

    async def create_user(self, username: str, password: str):
        existing_user = await self.user_repo.get_by_username(username)

        if existing_user:
            raise UserAlreadyExistsError("Пользователь уже существует")

        user = await self.user_repo.create(
            username=username,
            password_hash=password
        )

        await self.db.commit()

        return user
    
    async def authenticate_user(self, username: str, password: str):
        user = await self.user_repo.get_by_username(username)

        if not user:
            raise UserNotFoundError("Неверный логин или пароль")

        if user.password_hash != password:
            raise InvalidCredentialsError("Неверный логин или пароль")

        return user


class TransactionService:
    def __init__(self, db:AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
    
    async def send_coin(self, from_user_id: int, to_username: str, amount: int):
        if amount <= 0:
            raise InvalidAmountError("Сумма должна быть больше нуля")

        async with self.db.begin():
            sender = await self.user_repo.get_by_id_for_update(from_user_id)
            receiver = await self.user_repo.get_by_username_for_update(to_username)

            if not sender:
                raise UserNotFoundError("Отправитель не найден")
            if not receiver:
                raise UserNotFoundError("Получатель не найден")
            if sender.id == receiver.id:
                raise SelfTransferError("Нельзя отправить самому себе")
            if sender.coins < amount:
                raise NotEnoughCoinsError("Недостаточно средств")

            sender.coins -= amount
            receiver.coins += amount

            await self.transaction_repo.create(
                from_user_id=sender.id,
                to_user_id=receiver.id,
                amount=amount
            )


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.purchase_history_repo = PurchaseHistoryRepository(db)

    async def buy_item(self, item_name: str, user_id: int):
        async with self.db.begin():
            user = await self.user_repo.get_by_id_for_update(user_id)
            
            if not user:
                raise UserNotFoundError("Пользователь не найден")

            item = await self.inventory_repo.get_merch_by_name(item_name)
            
            if not item:
                raise ItemNotFoundError("Товар не найден")

            if user.coins < item.price:
                raise NotEnoughCoinsError("Недостаточно средств для покупки")

            user.coins -= item.price

            inventory_item = await self.inventory_repo.get_user_item_for_update(
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

            await self.purchase_history_repo.create_purchase(
                user_id=user_id,
                merch_id=item.id,
                quantity=1
            )



