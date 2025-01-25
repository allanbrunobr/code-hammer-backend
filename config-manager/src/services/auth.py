from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..adapters.dtos import UserDTO, LoginRequest
from ..domain import User
from ..repositories import UserRepository
from ..core.db.database import get_db
from ..utils import Environment

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def create_jwt_token(user: User) -> str:
    to_encode = {"sub": str(user.uuid)}
    expire = datetime.utcnow() + timedelta(minutes=int(Environment.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Environment.get("SECRET_KEY"), algorithm=Environment.get("ALGORITHM"))
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user_repository = UserRepository()
    user = user_repository.get_user_by_email(db, email)
    if user and pwd_context.verify(password, user.password):
        return user
    return None

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_repository = UserRepository()
    user = user_repository.get_user_by_email(db, user_uuid)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def validate_jwt_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        user_uuid: str = payload.get("sub")
        return user_uuid
    except JWTError:
        return None
