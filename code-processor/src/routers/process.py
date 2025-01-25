from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import logging
from typing import Any, Optional

from ..adapters.dtos import ProcessRequestDTO, MessageDTO
from ..core.db.database import get_db
from ..services import ProcessService
from ..services import UserService

user_service = UserService()
process_service = ProcessService()

logger = logging.getLogger(__name__)

process_router = APIRouter(
    prefix="/process",
    tags=["Process"],
)

@process_router.post("/")
def process(
    process_request: ProcessRequestDTO,
    db: Session = Depends(get_db)
):
    """
        Endpoint to process a request.

        Args:
            process_request (ProcessRequestDTO): Processing request data.
            current_user (UserDTO): Authenticated user.
            process_service (ProcessService): Processing service.
            user_service (UserService): User service.

        Returns:
            ResponseModel: Response with success or error status.
    """
    try:
        user = user_service.get_user_by_email(db, process_request.email)
        if(not user):
            return JSONResponse(content={"message": "User not found."}, status_code=404)
        if(user_service.verify_user_is_active(db, user.email)):
            return JSONResponse(content={"message": "User not active."}, status_code=401)

        user_prefer = user_service.get_user_prefer(user)
        process_service.sent_message(user_prefer)
        return JSONResponse(content={"status": "success"}, status_code=200)

    except Exception as e:
        logger.exception(f"Ocorreu um erro: {e}")
        return JSONResponse(content={"message": "internal error server."}, status_code=500)
