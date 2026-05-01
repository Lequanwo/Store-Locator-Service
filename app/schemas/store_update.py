from typing import Optional, List
from pydantic import BaseModel


class StoreUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    services: Optional[List[str]] = None
    status: Optional[str] = None

    hours_mon: Optional[str] = None
    hours_tue: Optional[str] = None
    hours_wed: Optional[str] = None
    hours_thu: Optional[str] = None
    hours_fri: Optional[str] = None
    hours_sat: Optional[str] = None
    hours_sun: Optional[str] = None

class StoreCreateRequest(StoreUpdateRequest):
    # store_id must be unique and follow format SXXXX where X is a digit
    store_id: str
    name: str
    store_type: str
    status: str
    latitude: float
    longitude: float
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str
    phone: str
    services: List[str]
    

    hours_mon: str
    hours_tue: str
    hours_wed: str
    hours_thu: str
    hours_fri: str
    hours_sat: str
    hours_sun: str
