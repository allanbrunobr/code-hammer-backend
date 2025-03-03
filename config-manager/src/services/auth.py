from datetime import datetime, timedelta
import logging
from fastapi import Depends, HTTPException, status
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import sys

from ..adapters.dtos import UserDTO, LoginRequest
from ..domain.users import User
from ..repositories.user import UserRepository
from ..core.db.database import get_db
from ..utils import Environment
from ..utils.logging_config import setup_logging

import firebase_admin
from firebase_admin import auth, credentials

# Configurar o logger
logger = setup_logging()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# Initialize Firebase Admin SDK
service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'keys', 'firebase-service-account.json')
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Looking for Firebase credentials at: {service_account_path}")
logger.debug(f"File exists: {os.path.exists(service_account_path)}")

if os.path.exists(service_account_path):
    try:
        logger.debug("Attempting to load Firebase credentials...")
        cred = credentials.Certificate(service_account_path)
        logger.debug("Firebase credentials loaded successfully")
        
        try:
            firebase_admin.initialize_app(cred)
            logger.debug("Firebase Admin SDK initialized successfully")
        except ValueError as e:
            logger.debug(f"Firebase Admin SDK already initialized: {e}")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Error loading Firebase credentials: {str(e)}", exc_info=True)
else:
    error_msg = f"Firebase credentials file not found at {service_account_path}"
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    logger.debug("=== Auth Debug ===")
    logger.debug(f"Received token length: {len(token) if token else 'None'}")
    
    if token:
        logger.debug(f"Token starts with: {token[:30]}...")
    else:
        logger.debug("No token received")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Remove 'Bearer ' se presente
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
            logger.debug("Removed 'Bearer ' prefix from token")

        if not token:
            logger.error("Token is empty after processing")
            raise credentials_exception

        # Add extensive debug logging
        try:
            # Verify Firebase ID token
            logger.debug(f"Attempting to verify token...")
            decoded_token = auth.verify_id_token(token)
            user_uid = decoded_token['uid']
            logger.info(f"Token decoded successfully. UID: {user_uid}")
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise

        # Try to get user by Firebase UID
        try:
            user_repository = UserRepository()
            logger.debug(f"Looking for user with firebase_uid: {user_uid}")
            user = user_repository.get_user_by_firebase_uid(db, user_uid)
            
            if user is None:
                logger.error(f"No user found for Firebase UID: {user_uid}")
                # Para fins de depuração, vamos returnar valores fixos se não encontrar o usuário
                # Isso é temporário e deve ser removido após a correção do problema
                from ..adapters.dtos import UserDTO
                logger.debug("Returning hardcoded user for debugging")
                # Criar um DTO simulando um usuário para continuar o fluxo
                return UserDTO(
                    id="f70cf81c-3d1d-4cf0-8598-91be25d49b1e",  # ID do usuário real
                    name="Debug User",
                    email="debug@test.com",
                    is_admin=True,  # Dar acesso admin para testes
                    firebase_uid=user_uid
                )
                # Na versão final, manter o código abaixo:
                # raise credentials_exception
            
            logger.debug(f"User found: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")
            raise

    except auth.InvalidIdTokenError as e:
        logger.error(f"Invalid Firebase ID token: {str(e)}", exc_info=True)
        raise credentials_exception from e
    except Exception as e:
        logger.error(f"Unexpected error validating token: {str(e)}", exc_info=True)
        raise credentials_exception from e

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user