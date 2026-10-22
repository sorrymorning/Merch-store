import redis.asyncio as redis
from app.core.config import settings





class RedisCache:
    def __init__(self, redis_url: str, default_ttl: int | None = 3600):
        self._redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis: redis.Redis | None = None

    async def init(self):
        """Инициализация пула соединений при старте приложения"""
        if self.redis is None:
            self.redis = redis.from_url(self._redis_url, decode_responses=True)


    async def close(self):
        """Закрытие соединений при остановке"""
        if self.redis is not None:
            await self.redis.aclose()

    async def get(self, key: str) -> str | None:
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        if not self.redis:
            return None
        expire = ttl if ttl is not None else self.default_ttl
        result = await self.redis.set(name=key, value=value, ex=expire)

        check = await self.redis.get(key)

    async def delete(self, key:str) -> None:
        if not self.redis:
            return None
        await self.redis.delete(key)



redis_cache = RedisCache(redis_url=settings.REDIS_URL)
