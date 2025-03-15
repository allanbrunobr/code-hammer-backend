import logging

from sqlalchemy.orm import Session
from typing import Optional, List

from ..adapters.dtos import UserCreateDTO, UserDTO, LoginRequest
from ..domain import User


class UserRepository:
    def __init__(self):
        pass

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def list_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def create_user(self, db: Session, user_data: UserCreateDTO) -> User:
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            country=user_data.country,
            language=user_data.language
        )
        new_user.set_password(user_data.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def update_user(self, db: Session, user_id: int, user_data: UserDTO) -> Optional[User]:
        user = self.get_user_by_id(db, user_id)
        if user:
            user.name = user_data.name
            user.email = user_data.email
            user.country = user_data.country
            user.language = user_data.language
            db.commit()
            db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: int) -> Optional[User]:
        user = self.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user

    def authenticate_user(self, db: Session, login_request: LoginRequest) -> Optional[User]:
        user = self.get_user_by_email(db, login_request.email)
        logging.error(user)
        if user and user.verify_password(login_request.password):
            return user
        return None

