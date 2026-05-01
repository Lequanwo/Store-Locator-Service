# import json
# from app.core.redis import redis_client

# CACHE_TTL = 300  # 5 minutes


# def make_cache_key(prefix: str, payload: dict) -> str:
#     return f"{prefix}:{json.dumps(payload, sort_keys=True)}"


# def get_cache(key: str):
#     try:
#         data = redis_client.get(key)
#         if data:
#             return json.loads(data)
#     except Exception:
#         return None


# def set_cache(key: str, value):
#     try:
#         redis_client.setex(key, CACHE_TTL, json.dumps(value))
#     except Exception:
#         pass

# =============================================================================
import json
from diskcache import Cache

CACHE_TTL = 300  # 5 minutes

cache = Cache("cache/store_cache")  # folder on disk


def make_cache_key(prefix: str, payload: dict) -> str:
    return f"{prefix}:{json.dumps(payload, sort_keys=True)}"


def get_cache(key: str):
    return cache.get(key, default=None)


def set_cache(key: str, value):
    cache.set(key, value, expire=CACHE_TTL)


def clear_cache():
    cache.clear()

#=============================================================================
# import time
# import json

# CACHE_TTL = 300
# cache_store = {}


# def make_cache_key(prefix: str, payload: dict) -> str:
#     return f"{prefix}:{json.dumps(payload, sort_keys=True)}"


# def get_cache(key: str):
#     item = cache_store.get(key)

#     if item is None:
#         return None

#     value, expires_at = item

#     if time.time() > expires_at:
#         del cache_store[key]
#         return None

#     return value


# def set_cache(key: str, value):
#     cache_store[key] = (value, time.time() + CACHE_TTL)