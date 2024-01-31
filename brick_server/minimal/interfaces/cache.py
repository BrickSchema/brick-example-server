import asyncio
from typing import Any

from aiocache import BaseCache, caches
from fastapi_rest_framework.config import settings


async def use_cache(key: str, fallback_func: Any, *args, **kwargs) -> Any:
    cache: BaseCache = caches.get("default")
    # print(settings.cache)
    if settings.cache:
        value = await cache.get(key)
    else:
        value = None
    if value is None:
        if asyncio.iscoroutinefunction(fallback_func):
            value = await fallback_func(*args, **kwargs)
        else:
            value = fallback_func(*args, **kwargs)
        if settings.cache:
            await cache.set(key, value)
            # logger.info("save cache {}: {}", key, value)
    else:
        pass
        # logger.info("load cache {}: {}", key, value)
    return value
