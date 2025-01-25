from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..adapters.dtos import PlanDTO, PlanCreateDTO
from ..services import PlanService
from ..core.db.database import get_db

plan_router = APIRouter(
    prefix="/plans",
    tags=["Plans"],
)

plan_service = PlanService()

@plan_router.get("/", response_model=List[PlanDTO])
def list_plans(db: Session = Depends(get_db)):
    return plan_service.list_plans(db)

@plan_router.post("/", response_model=PlanDTO)
def create_plan_endpoint(plan: PlanCreateDTO, db: Session = Depends(get_db)):
    return plan_service.create_plan(db, plan)

@plan_router.get("/{plan_id}", response_model=PlanDTO)
def get_plan(plan_id: UUID, db: Session = Depends(get_db)):
    return plan_service.get_plan(db, plan_id)

@plan_router.put("/{plan_id}", response_model=PlanDTO)
def update_plan_endpoint(plan_id: UUID, plan: PlanCreateDTO, db: Session = Depends(get_db)):
    return plan_service.update_plan(db, plan_id, plan)

@plan_router.delete("/{plan_id}", response_model=PlanDTO)
def delete_plan_endpoint(plan_id: UUID, db: Session = Depends(get_db)):
    return plan_service.delete_plan(db, plan_id)
