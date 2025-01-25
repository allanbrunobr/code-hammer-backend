from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..domain import Plan
from ..adapters.dtos import PlanCreateDTO

class PlanRepository:
    def get_plan_by_id(self, db: Session, plan_id: UUID) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.uuid == plan_id).first()

    def list_plans(self, db: Session) -> List[Plan]:
        return db.query(Plan).all()

    def create_plan(self, db: Session, plan_data: PlanCreateDTO) -> Plan:
        new_plan = Plan(**plan_data.dict())
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return new_plan

    def update_plan(self, db: Session, plan_id: UUID, plan_data: PlanCreateDTO) -> Optional[Plan]:
        plan = self.get_plan_by_id(db, plan_id)
        if plan:
            for key, value in plan_data.dict().items():
                setattr(plan, key, value)
            db.commit()
            db.refresh(plan)
        return plan

    def delete_plan(self, db: Session, plan_id: UUID) -> Optional[Plan]:
        plan = self.get_plan_by_id(db, plan_id)
        if plan:
            db.delete(plan)
            db.commit()
        return plan
