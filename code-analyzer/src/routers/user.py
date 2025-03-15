from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import requests
import os
import logging
from uuid import UUID

from src.domain import Token
from src.domain.users import User, LoginRequest
from src.services.auth import authenticate_user, create_jwt_token, get_current_user
from src.services.user_service_mock import get_user_by_id_mock, update_user_mock, delete_user_mock, \
    list_users_mock, fake_users_db, create_user_mock
from src.adapters.http_client import ConfigManagerClient

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@user_router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@user_router.post("/", response_model=User)
def create_user_endpoint(user: User):
    return create_user_mock(user)

@user_router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    db_user = get_user_by_id_mock(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.get("/{user_id}/subscription")
def get_user_subscription(user_id: str):
    """
    Obtém informações da assinatura do usuário.
    Este endpoint faz uma requisição ao config-manager para buscar os dados.
    """
    logging.info(f"Received request for subscription of user {user_id}")
    return ConfigManagerClient.get_user_subscription(user_id)

@user_router.put("/{user_id}", response_model=User)
def update_user_endpoint(user_id: int, user: User):
    db_user = update_user_mock(user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.delete("/{user_id}", response_model=User)
def delete_user_endpoint(user_id: int):
    db_user = delete_user_mock(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.get("/", response_model=List[User])
def list_users_endpoint():
    return list_users_mock()

@user_router.post("/token")
async def login(login_request: LoginRequest):
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_jwt_token(user)
    return {"access_token": access_token}

@user_router.get("/profile", response_model=User)
def read_profile(current_user: Token = Depends(get_current_user)):
    # Aqui você pode acessar o usuário autenticado e retornar suas informações
    user = fake_users_db.get(current_user.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
