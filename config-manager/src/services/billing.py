from fastapi import HTTPException
import uuid

from ..adapters.dtos import BillingDTO, BillingCreateDTO
from ..repositories import BillingRepository

class BillingService:
    def __init__(self):
        self.repository = BillingRepository()

    def get_billing(self, billing_id: uuid.UUID) -> BillingDTO:
        billing = self.repository.get_billing_by_id(billing_id)
        if not billing:
            raise HTTPException(status_code=404, detail="Billing record not found")
        return billing

    def create_billing(self, billing_data: BillingCreateDTO) -> BillingDTO:
        new_billing = self.repository.create_billing(billing_data)
        return new_billing

    def update_billing(self, billing_id: uuid.UUID, billing_data: BillingCreateDTO) -> BillingDTO:
        updated_billing = self.repository.update_billing(billing_id, billing_data)
        if not updated_billing:
            raise HTTPException(status_code=404, detail="Billing record not found")
        return updated_billing

    def delete_billing(self, billing_id: uuid.UUID) -> BillingDTO:
        deleted_billing = self.repository.delete_billing(billing_id)
        if not deleted_billing:
            raise HTTPException(status_code=404, detail="Billing record not found")
        return deleted_billing

    def list_billings(self) -> list[BillingDTO]:
        return self.repository.list_billings()
