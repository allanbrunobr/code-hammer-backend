from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..domain import Plan
from ..domain.plan_periods import PlanPeriod
from ..adapters.dtos import PlanCreateDTO

class PlanRepository:
    def get_plan_by_id(self, db: Session, plan_id: UUID) -> Optional[Plan]:
        return db.query(Plan).filter(Plan.id == plan_id).first()

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

    def get_plan_period(self, db: Session, plan_id: UUID, period_id: UUID) -> Optional[PlanPeriod]:
        """
        Busca um período de plano específico pelo ID do plano e ID do período.
        
        Args:
            db: Sessão do banco de dados.
            plan_id: ID do plano.
            period_id: ID do período.
            
        Returns:
            Optional[PlanPeriod]: O período de plano encontrado, ou None se não encontrado.
        """
        return db.query(PlanPeriod).filter(
            PlanPeriod.plan_id == plan_id,
            PlanPeriod.period_id == period_id
        ).first()
