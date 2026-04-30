import math
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from geopy.distance import geodesic

from app.db.database import get_db
from app.models.store import Store
from app.schemas.search import StoreSearchRequest

from fastapi import HTTPException
from app.services.geocoding import geocode_address, geocode_postal_code

from fastapi import APIRouter, Depends, Request
from app.core.limiter import limiter

from app.core.cache import make_cache_key, get_cache, set_cache

router = APIRouter(prefix="/api/stores", tags=["Store Search"])


@router.post("/search")
@limiter.limit("10/minute")
@limiter.limit("100/hour")
def search_stores(
    request: Request,  # MUST be named "request"
    body: StoreSearchRequest,  # rename your schema
    db: Session = Depends(get_db)
):
    # lat = request.latitude
    # lon = request.longitude

    searched_location = None

    if body.latitude is not None and body.longitude is not None:
        lat = body.latitude
        lon = body.longitude
        searched_location = {
            "input_type": "coordinates",
            "latitude": lat,
            "longitude": lon,
        }

    elif body.postal_code:
        geo = geocode_postal_code(body.postal_code)

        if not geo:
            raise HTTPException(status_code=400, detail="Could not geocode postal code")

        lat = geo["latitude"]
        lon = geo["longitude"]
        searched_location = {
            "input_type": "postal_code",
            "postal_code": body.postal_code,
            **geo,
        }

    elif body.address:
        geo = geocode_address(body.address)

        if not geo:
            raise HTTPException(status_code=400, detail="Could not geocode address")

        lat = geo["latitude"]
        lon = geo["longitude"]
        searched_location = {
            "input_type": "address",
            "address": body.address,
            **geo,
        }

    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either latitude/longitude, postal_code, or address",
        )

    radius = min(body.radius_miles or 10, 100)

    # Create a cache key based on search parameters
    cache_payload = {
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "radius": radius,
            "services": sorted(body.services or []),
            "store_types": sorted(body.store_types or []),
        }

    cache_key = make_cache_key("store_search", cache_payload)

    cached_response = get_cache(cache_key)
    if cached_response:
        print("✅ Store search cache hit")
        return cached_response
    
    print("Store search cache miss")

    # 1. Bounding box
    lat_delta = radius / 69.0
    lon_delta = radius / (69.0 * math.cos(math.radians(lat)))

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    # 2. SQL pre-filter
    query = db.query(Store).filter(
        Store.status == "active",
        Store.latitude.between(min_lat, max_lat),
        Store.longitude.between(min_lon, max_lon),
    )

    # 3. store_types filter: OR logic
    if body.store_types:
        query = query.filter(Store.store_type.in_(body.store_types))
    
    candidate_stores = query.all()

    results = []

    for store in candidate_stores:
        # 4. services filter: AND logic
        if body.services:
            store_services = set((store.services or "").split("|"))
            required_services = set(body.services)

            if not required_services.issubset(store_services):
                continue
                
        # check if store is open based on current day and hours - OPTIONAL ENHANCEMENT


        # 5. Exact distance
        distance = geodesic(
            (lat, lon),
            (store.latitude, store.longitude),
        ).miles

        if distance <= radius:
            results.append({
                "store_id": store.store_id,
                "name": store.name,
                "store_type": store.store_type,
                "status": store.status,
                "address": {
                    "street": store.address_street,
                    "city": store.address_city,
                    "state": store.address_state,
                    "postal_code": store.address_postal_code,
                    "country": store.address_country,
                },
                "phone": store.phone,
                "services": store.services.split("|") if store.services else [],
                "hours": {
                    "mon": store.hours_mon,
                    "tue": store.hours_tue,
                    "wed": store.hours_wed,
                    "thu": store.hours_thu,
                    "fri": store.hours_fri,
                    "sat": store.hours_sat,
                    "sun": store.hours_sun,
                },
                "distance_miles": round(distance, 2),
            })

    # 6. Sort nearest first
    results.sort(key=lambda x: x["distance_miles"])

    response = {
        "metadata": {
            "searched_location": searched_location,
            "radius_miles": radius,
            "services": body.services,
            "store_types": body.store_types,
            "result_count": len(results),
            "cache": "miss",
        },
        "results": results,
    }

    set_cache(cache_key, response)

    return response