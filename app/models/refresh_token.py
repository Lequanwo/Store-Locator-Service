from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.db.database import Base
import uuid

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_hash = Column(String, primary_key=True, index=True)
    # user_id = Column(String, nullable=False)
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)

    # id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # token_hash = Column(String, unique=True, nullable=False, index=True)

    # user_id = Column(String, ForeignKey("users.user_id"), nullable=False)

    