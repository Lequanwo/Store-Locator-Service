from sqlalchemy import Column, String, Boolean
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, marketer, viewer
    is_active = Column(Boolean, default=True)