import json
from app.core.redis import redis_client

CACHE_TTL = 300  # 5 minutes


def make_cache_key(prefix: str, payload: dict) -> str:
    return f"{prefix}:{json.dumps(payload, sort_keys=True)}"


def get_cache(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        return None


def set_cache(key: str, value):
    try:
        redis_client.setex(key, CACHE_TTL, json.dumps(value))
    except Exception:
        pass