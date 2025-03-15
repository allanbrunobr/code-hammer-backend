from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from typing import Optional, Union
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..domain import User, Token
from ..services.user_service_mock import get_user_by_username_mock
from ..utils import Environment

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token", auto_error=True)

class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    """
    Classe para autenticação opcional com OAuth2.
    Se o token não for fornecido ou for inválido, retorna None em vez de lançar uma exceção.
    """
    def __init__(self, tokenUrl: str, auto_error: bool = False):
        super().__init__(tokenUrl=tokenUrl, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param

optional_oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/users/token")


def create_jwt_token(user: User) -> str:
    to_encode = {"sub": user.username}
    expire = datetime.utcnow() + timedelta(minutes=int(Environment.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Environment.get("SECRET_KEY"), algorithm=Environment.get("ALGORITHM"))
    return encoded_jwt

def authenticate_user(username: str, password: str) -> Optional[User]:
    # Implemente esta função para buscar o usuário com base no nome de usuário.
    user = get_user_by_username_mock(username)  # Modifique para usar a implementação real
    if user and pwd_context.verify(password, user.password):
        return user
    return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:

            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user = get_user_by_username_mock(username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Token = Depends(get_current_user)) -> User:
    user = get_user_by_username_mock(current_user.username)  # Modifique para usar a implementação real
    if user is None or user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def validate_jwt_token(token: str) -> Optional[Token]:
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            return None
        return Token(username=username)
    except JWTError:
        return None

def get_optional_current_user(token: Optional[str] = Depends(optional_oauth2_scheme)) -> Optional[User]:
    """
    Função para obter o usuário atual de forma opcional.
    Se o token não for fornecido ou for inválido, retorna None em vez de lançar uma exceção.
    """
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = get_user_by_username_mock(username)
        return user
    except JWTError:
        return None

def get_user_id_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Extrai o ID do usuário a partir do token JWT.
    
    Para simplificar, estamos assumindo que o username no token é o ID do usuário.
    Em uma implementação real, você pode precisar buscar o ID do usuário com base no username.
    
    Args:
        token: Token JWT
        
    Returns:
        str: ID do usuário
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Environment.get("SECRET_KEY"), algorithms=[Environment.get("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Em uma implementação real, você pode buscar o ID do usuário com base no username
        # Por simplicidade, estamos assumindo que o username é o ID do usuário
        return username
    except JWTError:
        raise credentials_exception
