import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.repository import (UserRepository,
                                        InventoryRepository,
                                        TransactionRepository,
                                        PurchaseHistoryRepository,
                                        MerchRepository)
from app.services.services_errors import (UserNotFoundError, 
                             NotEnoughCoinsError, 
                             SelfTransferError,
                             ItemNotFoundError,
                             UserAlreadyExistsError,
                             InvalidCredentialsError
                                )
from app.cache.cache import RedisCache, redis_cache
import json
import logging



logger = logging.getLogger(__name__)



class UserService:
    def __init__(self, db:AsyncSession, cache: RedisCache = redis_cache):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.cache = redis_cache

    async def get_user(self, user_id:int):
        cache_key = f"user:info:{user_id}"

        cached_user = await self.cache.get(cache_key)
        if cached_user is not None:
            return cached_user

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.info("User with id: %s. Not Found", user_id)
            raise UserNotFoundError("Пользователь не найден")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            logger.info("User with id: %s. Not Found",user_id)
            raise UserNotFoundError("Пользователь не найден")


        inventory_rows, sent_rows, received_rows = await asyncio.gather( self.inventory_repo.get_inventory(user_id),
            self.transaction_repo.get_history_from_user(user_id),
            self.transaction_repo.get_history_to_user(user_id)
        )
        logger.info("User information successfully retrieved: %s",user_id)

        result =  {
            "coins": user.coins,
            "inventory": [
                {"type": row.type, "quantity": row.quantity} for row in inventory_rows
            ],
            "coinHistory": {
                "received": [{"fromUser": row.fromUser, "amount": row.amount} for row in received_rows],
                "sent": [{"toUser": row.toUser, "amount": row.amount} for row in sent_rows]
            }
        }

        await self.cache.set(
            cache_key,
            result,
            ttl=60,
        )

        logger.info(
            "User information successfully retrieved: %s", user_id
        )
        return result

    async def create_user(self, username: str, password: str):
        existing_user = await self.user_repo.get_by_username(username)

        if existing_user:
            logger.warning("Registration attempt with existing username: %s", username)
            raise UserAlreadyExistsError("Пользователь уже существует")

        user = await self.user_repo.create(
            username=username,
            password_hash=password
        )
        await self.db.commit()
        logger.info("Successfully created user: %s",user.id)
        return user
    
    async def authenticate_user(self, username: str, password: str):
        user = await self.user_repo.get_by_username(username)

        if not user:
            logger.warning("Authentication failed: user not found for username=%s", username)
            raise UserNotFoundError("Неверный логин или пароль")

        if user.password_hash != password:
            logger.warning("Authentication failed: invalid password for user_id=%s", user.id)
            raise InvalidCredentialsError("Неверный логин или пароль")

        logger.info("Authentication succes for user_id: %s",user.id)
        return user

class MerchService:
    def __init__(self,db: AsyncSession, cache: RedisCache = redis_cache):
        self.db = db
        self.merch_repo = MerchRepository(db)
        self.cache = redis_cache


    async def create_merch(self, merch_name:str, merch_price:int):
        merch = await self.merch_repo.create_merch(
            merch_name = merch_name,
            merch_price = merch_price
        )
        await self.db.commit()
        logger.info("Successfully created merch: %s",merch_name)
        return merch

    async def get_merch_by_name(self, name: str) -> dict | None:
        cache_key = f"merch:{name}"

        cached_data = await self.cache.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        merch = await self.merch_repo.get_merch_by_name(name)

        if not merch:
            return None

        merch_dict = {
            "id": merch.id,
            "name": merch.name,
            "price": merch.price
        }

        await self.cache.set(
            cache_key,
            json.dumps(merch_dict)
        )
        logger.info("Successfully got merch: %s", name)
        return merch
    

class TransactionService:
    def __init__(self, db:AsyncSession, cache: RedisCache = redis_cache):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.cache = redis_cache
    
    async def send_coin(self, from_user_id: int, to_username: str, amount: int):
        if amount <= 0:
            logger.warning("Invalid coin amount attempt: amount=%s", amount)
            raise InvalidAmountError("Сумма должна быть больше нуля")
        try:
            async with self.db.begin():
                sender = await self.user_repo.get_by_id_for_update(from_user_id)
                receiver = await self.user_repo.get_by_username_for_update(to_username)

                if not sender:
                    logger.warning("Transfer failed: sender not found, user_id=%s", from_user_id)
                    raise UserNotFoundError("Отправитель не найден")
                if not receiver:
                    logger.warning("Transfer failed: receiver not found, username=%s", to_username)
                    raise UserNotFoundError("Получатель не найден")
                if sender.id == receiver.id:
                    logger.warning("Self-transfer attempt blocked for user_id=%s", from_user_id)
                    raise SelfTransferError("Нельзя отправить самому себе")
                if sender.coins < amount:
                    logger.warning(
                        "Not enough coins for transfer: user_id=%s, has=%s, needed=%s",
                        sender.id,
                        sender.coins,
                        amount,
                    )
                    raise NotEnoughCoinsError("Недостаточно средств")

                sender.coins -= amount
                receiver.coins += amount

                await self.transaction_repo.create(
                    from_user_id=sender.id,
                    to_user_id=receiver.id,
                    amount=amount
                )

                logger.info(
                    "Coins successfully transferred: from_user_id=%s, to_user_id=%s, amount=%s",
                    sender.id,
                    receiver.id,
                    amount
                )
            for user_id in (from_user_id, receiver.id):
                try:
                    await self.cache.delete(f"user:info:{user_id}")
                except Exception:
                    logger.exception(
                        "Failed to invalidate user cache: user_id=%s",
                        user_id,
                    )

        except Exception:
            logger.exception(
                "Unexpected error during coin transfer: from_user_id=%s, to_username=%s, amount=%s",
                from_user_id,
                to_username,
                amount,
            )
            raise


class InventoryService:
    def __init__(self, db: AsyncSession, cache: RedisCache = redis_cache):
        self.db = db
        self.user_repo = UserRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.merch_service = MerchService(db=self.db)
        self.purchase_history_repo = PurchaseHistoryRepository(db)
        self.cache = redis_cache

    async def buy_item(self, item_name: str, user_id: int):
        try:
            async with self.db.begin():
                user = await self.user_repo.get_by_id_for_update(user_id)
                
                if not user:
                    logger.warning("Purchase failed: user not found, user_id=%s", user_id)
                    raise UserNotFoundError("Пользователь не найден")

                item = await self.merch_service.get_merch_by_name(item_name)

                if not item:
                    logger.warning("Purchase failed: item not found, item_name=%s", item_name)
                    raise ItemNotFoundError("Товар не найден")

                if user.coins < item.price:
                    logger.warning(
                        "Not enough coins to buy item: user_id=%s, item=%s, price=%s, balance=%s",
                        user_id,
                        item.name,
                        item.price,
                        user.coins
                    )
                    raise NotEnoughCoinsError("Недостаточно средств для покупки")

                user.coins -= item.price

                inventory_item = await self.inventory_repo.get_user_item_for_update(
                    user_id=user_id,
                    merch_id=item.id
                )

                if inventory_item:
                    inventory_item.quantity += 1
                    logger.info(
                        "Increased item quantity in inventory: user_id=%s, merch_id=%s, new_qty=%s",
                        user_id,
                        item.id,
                        inventory_item.quantity,
                    )
                else:
                    await self.inventory_repo.create_purchase(
                        user_id=user_id,
                        merch_id=item.id
                    )
                    logger.info(
                        "Created new inventory record: user_id=%s, merch_id=%s",
                        user_id,
                        item.id,
                    )

                await self.purchase_history_repo.create_purchase(
                    user_id=user_id,
                    merch_id=item.id,
                    quantity=1
                )
                
                logger.info(
                    "Purchase completed successfully: user_id=%s, item=%s, price=%s",
                    user_id,
                    item.name,
                    item.price,
                )
            try:
                await self.cache.delete(f"user:info:{user_id}")
            except Exception:
                logger.exception(
                    "Failed to invalidate user cache: user_id=%s",
                    user_id,
                )
        except Exception:
            logger.exception(
                "Unexpected error during buy item: user_id=%s, item=%s",
                user_id,
                item_name
            )
            raise



