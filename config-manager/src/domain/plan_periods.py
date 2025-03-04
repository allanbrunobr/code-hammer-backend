import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.db.database import Base


class PlanPeriod(Base):
    __tablename__ = 'plan_periods'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('plans.id'), nullable=False)
    period_id = Column(UUID(as_uuid=True), ForeignKey('periods.id'), nullable=False)
    price = Column(Numeric, nullable=False)
    currency = Column(String(10), nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
