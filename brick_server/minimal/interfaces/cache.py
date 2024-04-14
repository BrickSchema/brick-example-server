import asyncio
from typing import Any

from aiocache import BaseCache, caches

from brick_server.minimal.config.manager import settings


async def use_cache(key: str, fallback_func: Any, *args, **kwargs) -> Any:
    cache: BaseCache = caches.get("default")
    # print(settings.CACHE)
    if settings.CACHE:
        value = await cache.get(key)
    else:
        value = None
    if value is None:
        if asyncio.iscoroutinefunction(fallback_func):
            value = await fallback_func(*args, **kwargs)
        else:
            value = fallback_func(*args, **kwargs)
        if settings.CACHE:
            await cache.set(key, value)
            # logger.info("save cache {}: {}", key, value)
    else:
        pass
        # logger.info("load cache {}: {}", key, value)
    return value


caches.set_config(
    {
        "default": {
            "cache": "aiocache.RedisCache",
            "endpoint": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DATABASE,
            "password": settings.REDIS_PASSWORD,
            "timeout": 1,
            "serializer": {"class": "aiocache.serializers.PickleSerializer"},
            "plugins": [
                {"class": "aiocache.plugins.HitMissRatioPlugin"},
                {"class": "aiocache.plugins.TimingPlugin"},
            ],
        }
    }
)
