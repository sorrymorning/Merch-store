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

            print("REDIS URL:", self._redis_url)
            print("REDIS PING:", await self.redis.ping())

    async def close(self):
        """Закрытие соединений при остановке"""
        if self.redis is not None:
            await self.redis.aclose()

    async def get(self, key: str) -> str | None:
        if not self.redis:
            raise RuntimeError("RedisCache не инициализирован! Вызовите await cache.init()")
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        if not self.redis:
            raise RuntimeError("RedisCache не инициализирован! Вызовите await cache.init()")
        expire = ttl if ttl is not None else self.default_ttl
        result = await self.redis.set(name=key, value=value, ex=expire)
        print("REDIS SET RESULT:", result)

        check = await self.redis.get(key)

        print("REDIS GET AFTER SET:", check)


redis_cache = RedisCache(redis_url=settings.REDIS_URL)
