from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..core.db import Base


class Billing(Base):
    __tablename__ = 'billings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    amount = Column(String(100), nullable=False)
    currency = Column(String(100))
    payment_date = Column(String(100))
    payment_method = Column(String(100))
    payment_status = Column(String(100))
    transaction_id = Column(String(100))
    plan_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
