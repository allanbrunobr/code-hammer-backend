# repositories/billing_repository.py
from ..domain import Billing
from ..adapters.dtos import BillingCreateDTO
from ..core.db import get_db
import uuid

class BillingRepository:
    def __init__(self):
        self.db = get_db()

    def get_billing_by_id(self, billing_id: uuid.UUID) -> Billing:
        try:
            return self.db.query(Billing).filter(Billing.uuid == billing_id).first()
        finally:
            self.db.close()

    def list_billings(self) -> list[Billing]:
        try:
            return self.db.query(Billing).all()
        finally:
            self.db.close()

    def create_billing(self, billing_data: BillingCreateDTO) -> Billing:
        try:
            new_billing = Billing(
                amount=billing_data.amount,
                currency=billing_data.currency,
                payment_date=billing_data.payment_date,
                payment_method=billing_data.payment_method,
                payment_status=billing_data.payment_status,
                transaction_id=billing_data.transaction_id,
                plan_id=billing_data.plan_id
            )
            self.db.add(new_billing)
            self.db.commit()
            self.db.refresh(new_billing)
            return new_billing
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    def update_billing(self, billing_id: uuid.UUID, billing_data: BillingCreateDTO) -> Billing:
        try:
            billing = self.db.query(Billing).filter(Billing.uuid == billing_id).first()
            if billing:
                billing.amount = billing_data.amount
                billing.currency = billing_data.currency
                billing.payment_date = billing_data.payment_date
                billing.payment_method = billing_data.payment_method
                billing.payment_status = billing_data.payment_status
                billing.transaction_id = billing_data.transaction_id
                billing.plan_id = billing_data.plan_id
                self.db.commit()
                self.db.refresh(billing)
            return billing
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            self.db.close()

    def delete_billing(self, billing_id: uuid.UUID) -> Billing:
        try:
            billing = self.db.query(Billing).filter(Billing.uuid == billing_id).first()
            if billing:
                self.db.delete(billing)
                self.db.commit()
            return billing
        finally:
            self.db.close()
