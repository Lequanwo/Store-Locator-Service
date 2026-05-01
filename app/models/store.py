from sqlalchemy import Column, String, Float, Index, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    store_type = Column(String, nullable=False)
    status = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    address_street = Column(String)
    address_city = Column(String)
    address_state = Column(String(10))
    address_postal_code = Column(String(10))
    address_country = Column(String(10))

    phone = Column(String)

    services = Column(String)  # "pharmacy|pickup|optical"

    hours_mon = Column(String)
    hours_tue = Column(String)
    hours_wed = Column(String)
    hours_thu = Column(String)
    hours_fri = Column(String)
    hours_sat = Column(String)
    hours_sun = Column(String)

   