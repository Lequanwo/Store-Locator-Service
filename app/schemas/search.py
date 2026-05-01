from typing import Optional, List
from pydantic import BaseModel


class StoreSearchRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    address: Optional[str] = None
    postal_code: Optional[str] = None

    radius_miles: Optional[float] = 10
    services: Optional[List[str]] = None
    store_types: Optional[List[str]] = None

    open_now: Optional[bool] = False