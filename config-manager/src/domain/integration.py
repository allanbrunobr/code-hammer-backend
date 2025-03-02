from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..core.db.database import Base


class Integration(Base):
    __tablename__ = 'integrations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    api_key = Column(String(100))
    repository = Column(String(100))
    repository_user = Column(String(100))
    repository_token = Column(String(100))
    repository_url = Column(String(100))
    analyze_types = Column(String(100))
    quality_level = Column(String(100))
    user_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class Config:
        orm_mode = True
