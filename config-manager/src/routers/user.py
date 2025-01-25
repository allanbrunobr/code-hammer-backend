import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..adapters.dtos import UserDTO, UserCreateDTO, LoginRequest
from ..services import UserService
from ..services.auth import get_current_user, authenticate_user, create_jwt_token
from ..core.db.database import get_db

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# Instanciar o serviço
user_service = UserService()


@user_router.get("/me", response_model=UserDTO)
def read_users_me(
    current_user: UserDTO = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

@user_router.post("/", response_model=UserDTO)
def create_user_endpoint(
    user: UserCreateDTO,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db, user)

@user_router.get("/{user_id}", response_model=UserDTO)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return user_service.get_user(db, user_id)

@user_router.put("/{user_id}", response_model=UserDTO)
def update_user_endpoint(
    user_id: int,
    user: UserDTO,
    db: Session = Depends(get_db)
):
    return user_service.update_user(db, user_id, user)

@user_router.delete("/{user_id}", response_model=UserDTO)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db)
):
    return user_service.delete_user(db, user_id)

@user_router.get("/", response_model=List[UserDTO])
def list_users_endpoint(
    db: Session = Depends(get_db)
):
    return user_service.list_users(db)

@user_router.post("/token")
async def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = user_service.authenticate_user(db, login_request)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_jwt_token(user)
    return {"access_token": access_token}
