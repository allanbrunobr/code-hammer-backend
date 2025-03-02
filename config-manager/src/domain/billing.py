from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from ..core.db.database import Base


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
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)  # Adicionando user_id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento
    user = relationship("User", backref="billings")
