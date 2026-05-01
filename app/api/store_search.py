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

def check_cache(searched_info, radius):
    cache_payload = {"searched_info": searched_info,"radius": radius}
    cache_key = make_cache_key("geocoding_results", cache_payload)
    cached_geo = get_cache(cache_key)
    if cached_geo is not None:
        return cached_geo
    return None

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
        if check_cache(body.postal_code, body.radius_miles):
            print("Store search geocoding cache hit")
            cached_geo = check_cache(body.postal_code, body.radius_miles)
            lat = cached_geo["latitude"]
            lon = cached_geo["longitude"]
            searched_location = {
                "input_type": "postal_code",
                "postal_code": body.postal_code,
                **cached_geo,
            }
        else:
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

            set_cache(make_cache_key("geocoding_results", {"searched_info": body.postal_code,"radius": body.radius_miles}), geo)

    elif body.address:
        if check_cache(body.address, body.radius_miles):
            print("Store search geocoding cache hit")
            cached_geo = check_cache(body.address, body.radius_miles)
            lat = cached_geo["latitude"]
            lon = cached_geo["longitude"]
            searched_location = {
                "input_type": "address",
                "address": body.address,
                **cached_geo,
            }
        else:
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

            set_cache(make_cache_key("geocoding_results", {"searched_info": body.address,"radius": body.radius_miles}), geo)

    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either latitude/longitude, postal_code, or address",
        )

    radius = min(body.radius_miles or 10, 100)

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
        
        # check if open now filter
        # print(f"Checking store {store.store_id} for open_now filter")
        if body.open_now:
            # print store id
            # print(f"Store {store.store_id} is being checked for open_now filter")
            from datetime import datetime
            # only take time into account, ignore date since hours are the same every day
            now = datetime.now()
            weekday = now.strftime("%a").lower()  
            # print(f"Store hours for {weekday}: {getattr(store, f'hours_{weekday}', None)}")
            hours_str = getattr(store, f"hours_{weekday}", None)

            if hours_str and hours_str.lower() != "closed":
                open_time_str, close_time_str = hours_str.split("-")
                open_time = datetime.strptime(open_time_str.strip(), "%H:%M").time()
                close_time = datetime.strptime(close_time_str.strip(), "%H:%M").time()

                if not (open_time <= now.time() <= close_time):
                    continue
            else:
                continue

        # 5. Exact distance
        # print(f"Calculating distance from searched location to store {store.store_id}")
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
        },
        "results": results,
    }

    

    return response