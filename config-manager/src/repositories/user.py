import logging
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from typing import Optional, List

from ..adapters.dtos.user import UserCreateDTO, UserDTO, UserUpdateDTO
import logging
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from typing import Optional, List

from ..adapters.dtos.user import UserCreateDTO, UserDTO, UserUpdateDTO
from ..domain.users import User


class UserRepository:
    def __init__(self):
        pass

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_firebase_uid(self, db: Session, firebase_uid: str) -> Optional[User]:
        return db.query(User).filter(User.firebase_uid == firebase_uid).first()

    def list_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def create_user(self, db: Session, user_data: UserCreateDTO) -> User:
        now = datetime.utcnow()
        new_user = User(
            id=uuid4(),
            name=user_data.name or user_data.email.split('@')[0],
            email=user_data.email,
            firebase_uid=user_data.firebase_uid,  # Set Firebase UID
            created_at=now,
            updated_at=now
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def update_user(self, db: Session, user_id: UUID, user_data: UserUpdateDTO) -> Optional[User]:
        user = self.get_user_by_id(db, user_id)
        if user:
            if user_data.name is not None:
                user.name = user_data.name
            if user_data.email is not None:
                user.email = user_data.email
            if user_data.country is not None:
                user.country = user_data.country
            if user_data.language is not None:
                user.language = user_data.language

            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: UUID) -> Optional[User]:
        user = self.get_user_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user

    def get_user_id_by_email(self, db: Session, email: str) -> Optional[UUID]:
        logging.info(f"Entering get_user_id_by_email with email: {email}")
        user = db.query(User).filter(User.email == email).first()
        logging.info(f"get_user_id_by_email: Query result: {user}")
        if user:
            logging.info(f"get_user_id_by_email: Returning user ID: {user.id}")
            return user.id
        logging.info("get_user_id_by_email: Returning None")
        return None
