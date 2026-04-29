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