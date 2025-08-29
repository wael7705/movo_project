import os
import asyncio
from typing import Optional

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover
    redis = None  # type: ignore

_redis: Optional["redis.Redis"] = None


def get_redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


async def get_redis() -> Optional["redis.Redis"]:
    global _redis
    if redis is None:
        return None
    if _redis is None:
        _redis = redis.from_url(get_redis_url())
    return _redis
