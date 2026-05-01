from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class StoreService(Base):
    __tablename__ = "store_services"

    store_id = Column(String, ForeignKey("stores.store_id", ondelete="CASCADE"), primary_key=True)
    service_name = Column(String(100), primary_key=True)

    store = relationship("Store", back_populates="services")