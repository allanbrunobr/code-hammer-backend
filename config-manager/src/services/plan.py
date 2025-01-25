from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from uuid import UUID

from ..adapters.dtos import PlanCreateDTO, PlanDTO
from ..repositories import PlanRepository


class PlanService:
    def __init__(self):
        self.repository = PlanRepository()

    def get_plan(self, db: Session, plan_id: UUID) -> PlanDTO:
        plan = self.repository.get_plan_by_id(db, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan

    def create_plan(self, db: Session, plan_data: PlanCreateDTO) -> PlanDTO:
        new_plan = self.repository.create_plan(db, plan_data)
        return new_plan

    def update_plan(self, db: Session, plan_id: UUID, plan_data: PlanCreateDTO) -> PlanDTO:
        updated_plan = self.repository.update_plan(db, plan_id, plan_data)
        if not updated_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return updated_plan

    def delete_plan(self, db: Session, plan_id: UUID) -> PlanDTO:
        deleted_plan = self.repository.delete_plan(db, plan_id)
        if not deleted_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return deleted_plan

    def list_plans(self, db: Session) -> List[PlanDTO]:
        return self.repository.list_plans(db)
