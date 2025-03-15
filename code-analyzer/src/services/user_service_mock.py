from typing import List, Optional
from pydantic import BaseModel
from passlib.context import CryptContext

from datetime import datetime, timedelta
from typing import Optional
from src.domain import UserGroup
from src.domain.users import User


# Simulação de armazenamento em memória
fake_users_db = {}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Função para hash de senha
def get_password_hash(password):
    return pwd_context.hash(password)

# Função para obter usuário do banco de dados fictício
def get_user_by_username_mock(username: str) -> Optional[User]:
    for user in fake_users_db.values():
        if user.username == username:
            return user
    return None


def create_user_mock(user: User) -> Optional[User]:
    # Verificar se o nome de usuário já existe
    if any(existing_user.username == user.username for existing_user in fake_users_db.values()):
        return None

    # Gerar um novo ID de usuário
    new_id = max(fake_users_db.keys(), default=0) + 1

    # Hash da senha do usuário
    user.password = get_password_hash(user.password)

    # Adicionar usuário ao banco de dados fictício
    fake_users_db[new_id] = user

    return user


def get_user_by_id_mock(user_id: int) -> Optional[User]:
    return fake_users_db.get(user_id)

def update_user_mock(user_id: int, user: User) -> Optional[User]:
    db_user = fake_users_db.get(user_id)
    if db_user:
        updated_user = db_user.copy(update=user.dict())
        fake_users_db[user_id] = updated_user
        return updated_user
    return None

def delete_user_mock(user_id: int) -> Optional[User]:
    return fake_users_db.pop(user_id, None)

def list_users_mock() -> List[User]:
    # Retorna todos os usuários no armazenamento em memória
    return list(fake_users_db.values())




