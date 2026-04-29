import time

_cache = {}


def get_cache(key: str):
    item = _cache.get(key)

    if not item:
        return None

    value, expire_at = item

    if time.time() > expire_at:
        del _cache[key]
        return None

    return value


def set_cache(key: str, value, ttl_seconds: int):
    expire_at = time.time() + ttl_seconds
    _cache[key] = (value, expire_at)