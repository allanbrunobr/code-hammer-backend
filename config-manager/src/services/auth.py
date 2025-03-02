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
    logger.debug(f"Received token: {token[:20]}...")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Remove 'Bearer ' se presente
        if token.startswith('Bearer '):
            token = token.split(' ')[1]

        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_uid = decoded_token['uid']
        
        logger.info(f"Token decoded successfully. UID: {user_uid}")

        # Try to get user by Firebase UID
        user_repository = UserRepository()
        user = user_repository.get_user_by_firebase_uid(db, user_uid)
        
        if user is None:
            logger.error(f"No user found for Firebase UID: {user_uid}")
            raise credentials_exception
            
        logger.debug(f"User found: {user.id}")
        return user

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