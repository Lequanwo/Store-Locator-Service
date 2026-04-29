import requests

from app.services.cache import get_cache, set_cache


GEOCODING_TTL_SECONDS = 30 * 24 * 60 * 60


def geocode_address(query: str):
    cache_key = f"geocode:{query.lower().strip()}"

    cached = get_cache(cache_key)
    if cached:
        print("✅ Geocoding cache hit")
        return cached

    print("🌐 Calling Nominatim API")

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "us",
    }

    headers = {
        "User-Agent": "store-locator-api"
    }

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    result = {
        "latitude": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"]),
        "display_name": data[0].get("display_name"),
    }

    set_cache(cache_key, result, GEOCODING_TTL_SECONDS)

    return result


def geocode_postal_code(postal_code: str):
    return geocode_address(f"{postal_code}, USA")