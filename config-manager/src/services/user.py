import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID

from ..adapters.dtos.user import UserCreateDTO, UserDTO, LoginRequest, UserUpdateDTO
from ..repositories.user import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def get_user(self, db: Session, user_id: UUID) -> UserDTO:
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

    def update_user(self, db: Session, user_id: UUID, user_data: UserUpdateDTO) -> UserDTO:
        updated_user = self.repository.update_user(db, user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    def delete_user(self, db: Session, user_id: UUID) -> UserDTO:
        deleted_user = self.repository.delete_user(db, user_id)
        if not deleted_user:
            raise HTTPException(status_code=404, detail="User not found")
        return deleted_user

    def list_users(self, db: Session) -> List[UserDTO]:
        return self.repository.list_users(db)

    def check_email_exists(self, db: Session, email: str) -> bool:
        user = self.repository.get_user_by_email(db, email)
        return user is not None

    def get_user_id_by_email(self, db: Session, email: str) -> Optional[UUID]:
        logging.info(f"Entering get_user_id_by_email with email: {email}")
        try:
            # Validação básica do email
            if not email:
                raise ValueError("Email cannot be empty")
            
            user_id = self.repository.get_user_id_by_email(db, email)
            logging.info(f"Exiting get_user_id_by_email with user_id: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Error in get_user_id_by_email: {str(e)}")
            raise
