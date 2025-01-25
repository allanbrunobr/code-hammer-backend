import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from ..adapters.dtos import UserCreateDTO, UserDTO, LoginRequest
from ..repositories import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def get_user(self, db: Session, user_id: int) -> UserDTO:
        user = self.repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(self, db: Session, user_data: UserCreateDTO) -> UserDTO:
        existing_user = self.repository.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = self.repository.create_user(db, user_data)
        return new_user

    def update_user(self, db: Session, user_id: int, user_data: UserDTO) -> UserDTO:
        updated_user = self.repository.update_user(db, user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    def delete_user(self, db: Session, user_id: int) -> UserDTO:
        deleted_user = self.repository.delete_user(db, user_id)
        if not deleted_user:
            raise HTTPException(status_code=404, detail="User not found")
        return deleted_user

    def list_users(self, db: Session) -> List[UserDTO]:
        return self.repository.list_users(db)

    def authenticate_user(self, db: Session, login_request: LoginRequest) -> UserDTO:
        return self.repository.authenticate_user(db, login_request)
